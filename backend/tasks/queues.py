"""Queue that plans the executions of the tasks.

A task in this queue turns into the executions that its tool or process needs,
which are enqueued in the executions queue. For the processes, the steps are also
chained here, so a step waits for the ones that provide the findings it consumes.
"""

from dataclasses import dataclass, field
from datetime import timedelta
from functools import cached_property
from typing import Any, Sequence

from django.core.exceptions import ValidationError
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
from security.validators.enums import Regex
from security.validators.target_validator import TargetValidator
from tasks.models import Task
from tools.enums import Intensity as IntensityValue
from tools.models import Intensity


@dataclass
class PlanJob:
    """Step of a process, with the steps that must be executed before it.

    Attributes:
        step: Step of the process to be executed.
        dependencies: Steps whose findings this one consumes.
        jobs: Jobs enqueued for this step, which the dependent steps wait for.
    """

    step: Step
    dependencies: list["PlanJob"] = field(default_factory=list)
    jobs: list[Job] = field(default_factory=list)

    @cached_property
    def inputs(self) -> Sequence[InputType]:
        """The input types that the configuration of this step accepts."""
        return InputType.objects.filter(inputs__argument__configuration=self.step.configuration).distinct()

    @cached_property
    def outputs(self) -> Sequence[InputType]:
        """The input types of the findings that this step reports."""
        return InputType.objects.filter(outputs__configuration=self.step.configuration).distinct()

    def add_dependency(self, dependency: "PlanJob") -> None:
        """Add a step that must be executed before this one.

        Args:
            dependency: Step whose findings this one consumes.
        """
        self.dependencies.append(dependency)

    def add_job(self, job: Job) -> None:
        """Add a job enqueued for this step.

        Args:
            job: Enqueued job, which the dependent steps wait for.
        """
        self.jobs.append(job)

    def __eq__(self, other: object) -> bool:
        """Check if another object plans the same step.

        Args:
            other: Object to compare with this one.

        Returns:
            Whether both plan the same step. False for any object of a different
            type.
        """
        if not isinstance(other, PlanJob):
            return False
        return self.step.id == other.step.id

    def __hash__(self) -> int:
        """Return a hash of the step, so each step is planned once."""
        return hash(self.step.id)


class TasksQueue(BaseScanQueue):
    """Queue that turns the tasks into the executions that they need.

    Attributes:
        name: Name of the RQ queue.
    """

    name = "tasks"

    def enqueue(self, task: Task) -> Job:
        """Enqueue a task, at the moment that it's scheduled for.

        Args:
            task: Task to enqueue, which is run right away when it isn't scheduled.

        Returns:
            The enqueued job, whose identifier is saved in the task so it can be
            cancelled while it's still scheduled.
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
    def consume(task: Task) -> Task | None:
        """Plan and enqueue the executions of one task.

        The task target is re-validated against the deny list before any
        execution is created, because targets are only validated when created
        and a deny list change or DNS rebinding afterwards could otherwise let a
        previously-saved target be scanned. A rejected target does not run: the
        task is kept and the rejection is recorded as skipped executions so its
        history survives and the reason is visible. Its scheduling is cleared so
        a recurring or scheduled task is not re-run against the denied target
        over and over.

        Args:
            task: Task to plan, as it was when the job was enqueued.

        Returns:
            The task, which the success callback needs to schedule its next
            repetition.
        """
        BaseScanQueue.logger.info(f"[Task] Task {task.id} has started")
        try:
            TargetValidator(Regex.TARGET)(task.target.target)
        except ValidationError as error:
            skipped_reason = " ".join(error.messages)
            TasksQueue.logger.warning(
                f"[Security] Task {task.id} target '{task.target.target}' was rejected at execution time: "
                f"{skipped_reason}"
            )
            dt = timezone.now()
            for configuration in (
                [task.configuration]
                if task.configuration
                else [step.configuration for step in task.process.steps.filter(configuration__deprecated=False)]
            ):
                Execution.objects.create(
                    task=task,
                    configuration=configuration,
                    status=Status.SKIPPED,
                    skipped_reason=skipped_reason,
                    start=dt,
                    end=dt,
                )
            task.start = dt
            task.end = dt
            task.repeat_in = None
            task.repeat_time_unit = None
            task.save(update_fields=["start", "end", "repeat_in", "repeat_time_unit"])
            return task
        if task.configuration:
            TasksQueue._consume_tool_task(task)
        elif task.process:
            TasksQueue._consume_process_task(task)
        return task

    @staticmethod
    def _consume_tool_task(task: Task) -> None:
        """Enqueue the executions of a task that runs one tool configuration.

        Args:
            task: Task whose inputs are distributed among its executions.
        """
        executions = TasksQueue.calculate_executions(
            task.configuration,
            [],
            task.get_scoped_target_ports(),
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
        """Enqueue the executions of a task that runs a process, chaining its steps.

        A step depends on another one when it accepts the findings that the other
        reports, so the executions of the dependent steps are enqueued waiting for
        the ones they need, and the independent steps run in parallel.

        Args:
            task: Task whose process steps are planned and enqueued.
        """
        plan: list[PlanJob] = []
        # Order steps by stage, input complexity, output complexity, and configuration ID
        # so that simpler tools are planned before the more complex ones depending on their output
        steps = (
            task.process.steps.filter(configuration__deprecated=False)
            .annotate(
                max_input=Max("configuration__arguments__inputs__type__id"),
                max_output=Max("configuration__outputs__type__id"),
            )
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
                            break  # One matching output type is enough to establish the dependency
                plan.append(item)
            else:
                # The step is never planned or enqueued, but a SKIPPED execution is still
                # created for it so the process history shows every step and why it didn't run
                Execution.objects.create(
                    task=task,
                    configuration=step.configuration,
                    status=Status.SKIPPED,
                    skipped_reason=f"Tool {step.configuration.tool.name} can't be executed with intensity {IntensityValue(task.intensity).name.capitalize()}",
                )
        for execution_job in plan:
            executions = TasksQueue.calculate_executions(
                execution_job.step.configuration,
                [],  # No findings from previous steps yet; those become available once dependencies run
                task.get_scoped_target_ports(),
                task.input_vulnerabilities.all(),
                task.input_technologies.all(),
                task.wordlists.all(),
            )
            for parameters in executions:
                execution = Execution.objects.create(task=task, configuration=execution_job.step.configuration)
                execution_job.add_job(
                    executions_queue.enqueue(
                        execution,
                        parameters.findings,
                        parameters.target_ports,
                        parameters.input_vulnerabilities,
                        parameters.input_technologies,
                        parameters.wordlists,
                        # Flatten the dependency jobs of every prerequisite PlanJob into one list
                        dependencies=sum([d.jobs for d in execution_job.dependencies], []),
                    )
                )

    @staticmethod
    def _scheduled_callback(job: Any, connection: Any, result: Task, *args: Any, **kwargs: Any) -> None:
        """Schedule the next repetition of a task that has just been planned.

        The repetitions are chained one by one instead of being scheduled all at
        once, and the interval is counted from the moment when the task was
        enqueued, so a slow execution doesn't delay the following ones.

        Args:
            job: Task job that just finished.
            connection: Redis connection used by RQ to run the callback.
            result: Task returned by the consume method. A task whose target was
              rejected comes back with its repetition cleared, so a denied target
              is not scheduled again.
            *args: Not used, accepted for compatibility with the RQ callbacks.
            **kwargs: Not used, accepted for compatibility with the RQ callbacks.
        """
        if result and result.repeat_in and result.repeat_time_unit:
            new_task = Task.objects.create(
                target=result.target,
                process=result.process,
                configuration=result.configuration,
                intensity=result.intensity,
                executor=result.executor,
                scheduled_at=result.enqueued_at + timedelta(**{result.repeat_time_unit.lower(): result.repeat_in}),
                repeat_in=result.repeat_in,
                repeat_time_unit=result.repeat_time_unit,
            )
            new_task.wordlists.set(result.wordlists.all())
            new_task.input_technologies.set(result.input_technologies.all())
            new_task.input_vulnerabilities.set(result.input_vulnerabilities.all())
            TasksQueue().enqueue(new_task)
            BaseScanQueue.logger.info(f"[Task] Recurring task {new_task.id} has been scheduled")
