"""Queue management for task processing and execution orchestration.

Provides queue-based task processing capabilities with support for both single
tool tasks and complex multi-step process tasks. Handles task scheduling,
dependency management, and execution planning.
"""

from dataclasses import dataclass
from datetime import timedelta
from functools import cached_property
from typing import Any, Sequence

from django.db.models import Max
from django.utils import timezone
from django_rq import job
from rq.job import Job

from executions.enums import Status
from executions.models import Execution
from executions.queues import ExecutionsQueue
from framework.queues import BaseScanQueue
from input_types.models import InputType
from processes.models import Step
from tasks.models import Task
from tools.enums import Intensity as IntensityValue
from tools.models import Intensity


# TODO: Test this:
@dataclass
class PlanJob:
    """Dataclass representing a planned job in a process execution workflow.

    Represents a single step in a multi-step process execution plan with
    dependency management and input/output type tracking for proper
    execution ordering and parameter passing.

    Attributes:
        step (Step): The process step to be executed
        dependencies (list): List of PlanJob dependencies that must complete first
        jobs (list): List of RQ Job objects associated with this plan job
    """

    step: Step
    dependencies = []
    jobs = []

    @cached_property
    def inputs(self) -> Sequence[InputType]:
        """Get input types required by this job's tool.

        Returns:
            Sequence[InputType]: Input types needed by the step's tool
        """
        return InputType.objects.filter(inputs__argument__tool=self.step.configuration.tool).distinct()

    @cached_property
    def outputs(self) -> Sequence[InputType]:
        """Get output types produced by this job's tool.

        Returns:
            Sequence[InputType]: Output types produced by the step's configuration
        """
        return InputType.objects.filter(outputs__configuration=self.step.configuration).distinct()

    def add_dependency(self, dependency: "PlanJob") -> None:
        """Add a dependency to this job.

        Args:
            dependency (PlanJob): The job that must complete before this job
        """
        self.dependencies.append(dependency)

    def add_job(self, job: Job) -> None:
        """Add a RQ job to this plan job.

        Args:
            dependency (Job): The RQ Job object to associate with this plan job
        """
        self.jobs.append(job)

    def __eq__(self, other: Any) -> bool:
        """Check equality based on step ID.

        Args:
            other (Any): Object to compare with

        Returns:
            bool: True if both have the same step ID
        """
        if not isinstance(other, PlanJob):
            return False
        return self.step.id == other.step.id

    def __hash__(self) -> int:
        """Generate hash based on step ID.

        Returns:
            int: Hash value for this PlanJob
        """
        return hash(self.step.id)


class TasksQueue(BaseScanQueue):
    """Queue manager for task processing and execution coordination.

    Manages the task execution queue with support for immediate and scheduled
    task execution, process planning, and recurring task management.

    Attributes:
        name (str): Name of the queue ("tasks")
    """

    name = "tasks"

    def enqueue(self, task: Task) -> Job:
        """Enqueue a task for immediate or scheduled execution.

        Handles both immediate task execution and scheduled task execution
        with proper queue management and callback setup.

        Args:
            task (Task): The task to enqueue for execution

        Returns:
            Job: The RQ Job object for the enqueued task
        """
        if task.scheduled_at:
            task.enqueued_at = task.scheduled_at
            job = self.queue.enqueue_at(task.scheduled_at, self.consume, task=task, on_success=self._scheduled_callback)
            self.logger.info(f"[Task] Task {task.id} will be enqueued at {task.scheduled_at}")
        else:
            task.enqueued_at = timezone.now()
            job = self.queue.enqueue(self.consume, task=task, on_success=self._scheduled_callback)
            self.logger.info(f"[Task] Task {task.id} has been enqueued")
        task.rq_job_id = job.id
        task.save(update_fields=["enqueued_at", "rq_job_id"])
        return job

    @staticmethod
    @job("tasks")
    def consume(task: Task) -> Task:
        """Process a task by creating and enqueuing executions.

        Main task processing function that handles both single tool tasks
        and multi-step process tasks. Creates execution records and
        enqueues them for processing.

        Args:
            task (Task): The task to process

        Returns:
            Task: The processed task
        """
        if task.executions:
            task.executions.clear()
        if task.configuration:
            TasksQueue._consume_tool_task(task)
        elif task.process:
            TasksQueue._consume_process_task(task)
        return task

    @staticmethod
    def _consume_tool_task(task: Task) -> None:
        """Process a single tool task by creating executions.

        Handles tasks that execute a single security tool with specific
        configuration and parameters.

        Args:
            task (Task): The single tool task to process
        """
        executions = TasksQueue.calculate_executions(
            task.configuration.tool,
            [],
            task.target.target_ports.all(),
            task.input_vulnerabilities.all(),
            task.input_technologies.all(),
            task.wordlists.all(),
        )
        executions_queue = ExecutionsQueue()
        for parameters in executions:
            execution = Execution.objects.create(task=task, configuration=task.configuration)
            executions_queue.enqueue(
                execution,
                parameters.findings,
                parameters.target_ports,
                parameters.input_vulnerabilities,
                parameters.input_technologies,
                parameters.wordlists,
            )

    @staticmethod
    def _consume_process_task(task: Task) -> None:
        """Process a multi-step process task with dependency management.

        Handles tasks that execute complete security processes with multiple
        steps, managing dependencies between steps and proper execution ordering.

        Args:
            task (Task): The process task to process
        """
        plan: list[PlanJob] = []
        steps = (
            Step.objects.annotate(
                max_input=Max("configuration__tool__arguments__inputs__type__id"),
                max_output=Max("configuration__outputs__type__id"),
            )
            .filter(process=task.process)
            .order_by("configuration__stage", "max_input", "max_output", "configuration__id")
        )
        executions_queue = ExecutionsQueue()
        for step in steps:
            item = PlanJob(step)
            if Intensity.objects.filter(tool=step.configuration.tool, value__lte=task.intensity).exists():
                for execution_job in plan:
                    for output in execution_job.outputs:
                        if output in item.inputs:
                            if execution_job not in item.dependencies:
                                item.add_dependency(execution_job)
                            break
                plan.append(item)
            else:
                Execution.objects.create(
                    task=task,
                    configuration=step.configuration,
                    status=Status.SKIPPED,
                    skipped_reason=f"Tool {step.configuration.tool.name} can't be executed with intensity {IntensityValue(task.intensity).name.capitalize()}",
                )
        for execution_job in plan:
            executions = TasksQueue.calculate_executions(
                execution_job["step"].configuration.tool,
                [],
                task.target.target_ports.all(),
                task.input_vulnerabilities.all(),
                task.input_technologies.all(),
                task.wordlists.all(),
            )
            for parameters in executions:
                execution = Execution.objects.create(task=task, configuration=execution_job["step"].configuration)
                execution_job.add_job(
                    executions_queue.enqueue(
                        execution,
                        parameters.findings,
                        parameters.target_ports,
                        parameters.input_vulnerabilities,
                        parameters.input_technologies,
                        parameters.wordlists,
                        dependencies=sum([d.jobs for d in execution_job.dependencies], []),
                    )
                )

    @staticmethod
    def _scheduled_callback(job: Any, connection: Any, result: Task, *args: Any, **kwargs: Any) -> None:
        """Callback function for handling recurring task scheduling.

        Handles automatic recreation of recurring tasks based on repeat
        configuration. Creates new tasks with the same parameters when
        a task completes and has repeat settings configured.

        Args:
            job (Any): The completed RQ job
            connection (Any): Redis connection
            result (Task): The completed task
            *args (Any): Additional positional arguments
            **kwargs (Any): Additional keyword arguments
        """
        if result and result.repeat_in and result.repeat_time_unit:
            new_task = Task.objects.create(
                target=result.target,
                process=result.process,
                configuration=result.configuration,
                intensity=result.intensity,
                executor=result.user,
                scheduled_at=result.enqueued_at + timedelta(**{result.repeat_time_unit.lower(): result.repeat_in}),
                repeat_in=result.repeat_in,
                repeat_time_unit=result.repeat_time_unit,
            )
            new_task.wordlists.set(result.wordlists.all())
            new_task.input_technologies.set(result.input_technologies.all())
            new_task.input_vulnerabilities.set(result.input_vulnerabilities.all())
            self = TasksQueue()
            job = self.queue.enqueue_at(
                result.enqueued_at, self.consume, task=result, on_success=self._scheduled_callback
            )
            BaseScanQueue.logger.info(f"[Task] Scheduled task {result.id} has been enqueued again")
            new_task.rq_job_id = job.id
            new_task.save(update_fields=["rq_job_id"])
