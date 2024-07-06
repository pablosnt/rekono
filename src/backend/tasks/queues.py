import logging
from datetime import timedelta
from typing import Any

from django.db.models import Max
from django.utils import timezone
from django_rq import job
from executions.enums import Status
from executions.models import Execution
from executions.queues import ExecutionsQueue
from framework.queues import BaseQueue
from input_types.models import InputType
from processes.models import Step
from rq.job import Job
from tasks.models import Task
from tools.models import Intensity

logger = logging.getLogger()


class TasksQueue(BaseQueue):
    name = "tasks"

    def enqueue(self, task: Task) -> Job:
        queue = self._get_queue()
        if task.scheduled_at:
            task.enqueued_at = task.scheduled_at
            job = queue.enqueue_at(
                task.scheduled_at,
                self.consume,
                task=task,
                on_success=self._scheduled_callback,
            )
            logger.info(
                f"[Task] Task {task.id} will be enqueued at {task.scheduled_at}"
            )
        else:
            task.enqueued_at = timezone.now()
            job = queue.enqueue(
                self.consume,
                task=task,
                on_success=self._scheduled_callback,
            )
            logger.info(f"[Task] Task {task.id} has been enqueued")
        task.rq_job_id = job.id
        task.save(update_fields=["enqueued_at", "rq_job_id"])
        return job

    @staticmethod
    @job("tasks")
    def consume(task: Task) -> Task:
        if task.executions:
            task.executions.clear()
        if task.configuration:
            TasksQueue._consume_tool_task(task)
        elif task.process:
            TasksQueue._consume_process_task(task)
        return task

    @staticmethod
    def _consume_tool_task(task: Task) -> None:
        executions = TasksQueue._calculate_executions(
            task.configuration.tool,
            [],
            task.target.target_ports.all(),
            task.target.input_vulnerabilities.all(),
            task.target.input_technologies.all(),
            task.wordlists.all(),
        )
        executions_queue = ExecutionsQueue()
        for parameters in executions or [{}]:
            execution = Execution.objects.create(
                task=task, configuration=task.configuration, group=1
            )
            executions_queue.enqueue(
                execution,
                [],
                parameters.get(1, []),
                parameters.get(2, []),
                parameters.get(3, []),
                parameters.get(4, []),
            )

    @staticmethod
    def _consume_process_task(task: Task) -> None:
        plan: list[dict[str, Any]] = []
        steps = (
            Step.objects.annotate(
                max_input=Max("configuration__tool__arguments__inputs__type__id"),
                max_output=Max("configuration__outputs__type__id"),
            )
            .filter(process=task.process)
            .order_by(
                "configuration__stage", "max_input", "max_output", "configuration__id"
            )
        )
        executions_queue = ExecutionsQueue()
        for step in steps:
            item = {
                "step": step,
                "inputs": InputType.objects.filter(
                    inputs__argument__tool=step.configuration.tool
                ).distinct(),
                "outputs": InputType.objects.filter(
                    outputs__configuration=step.configuration
                ).distinct(),
                "dependencies": [],
                "jobs": [],
                "group": 1,
            }
            if Intensity.objects.filter(
                tool=step.configuration.tool, value__lte=task.intensity
            ).exists():
                for execution_job in plan:
                    for output in execution_job.get("outputs", []):
                        if output in item.get("inputs", []):
                            item["group"] = max(
                                [item["group"], execution_job["group"] + 1]
                            )
                            if execution_job["step"].id not in [
                                d["step"].id for d in item["dependencies"]
                            ]:
                                item["dependencies"].append(execution_job)
                            break
                plan.append(item)
            else:
                Execution.objects.create(
                    task=task,
                    configuration=step.configuration,
                    group=1,
                    status=Status.SKIPPED,
                    skipped_reason=f"Tool {step.configuration.tool.name} can't be executed with intensity {task.intensity.name.capitalize()}",
                )
        for execution_job in plan:
            executions = TasksQueue._calculate_executions(
                execution_job["step"].configuration.tool,
                [],
                task.target.target_ports.all(),
                task.target.input_vulnerabilities.all(),
                task.target.input_technologies.all(),
                task.wordlists.all(),
            )
            for parameters in executions or [{}]:
                execution = Execution.objects.create(
                    task=task,
                    configuration=execution_job["step"].configuration,
                    group=execution_job["group"],
                )
                execution_job["jobs"].append(
                    executions_queue.enqueue(
                        execution,
                        parameters.get(0, []),
                        parameters.get(1, []),
                        parameters.get(2, []),
                        parameters.get(3, []),
                        parameters.get(4, []),
                        dependencies=sum(
                            [d["jobs"] for d in execution_job["dependencies"]], []
                        ),
                    )
                )

    @staticmethod
    def _scheduled_callback(
        job: Any, connection: Any, result: Task, *args: Any, **kwargs: Any
    ) -> None:
        if result and result.repeat_in and result.repeat_time_unit:
            new_task = Task.objects.create(
                target=result.target,
                process=result.process,
                configuration=result.configuration,
                intensity=result.intensity,
                executor=result.user,
                scheduled_at=result.enqueued_at
                + timedelta(**{result.repeat_time_unit.lower(): result.repeat_in}),
                repeat_in=result.repeat_in,
                repeat_time_unit=result.repeat_time_unit,
            )
            new_task.wordlists.set(result.wordlists.all())
            instance = TasksQueue()
            job = instance._get_queue().enqueue_at(
                result.enqueued_at,
                instance.consume,
                task=result,
                on_success=instance._scheduled_callback,
            )
            logger.info(f"[Task] Scheduled task {result.id} has been enqueued again")
            new_task.rq_job_id = job.id
            new_task.save(update_fields=["rq_job_id"])
