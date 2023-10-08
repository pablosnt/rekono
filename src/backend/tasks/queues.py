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
    def __init__(self) -> None:
        super().__init__("tasks-queue")
        self.executions_queue = ExecutionsQueue()

    def enqueue(self, task: Task) -> Job:
        if task.scheduled_at:
            task.enqueued_at = task.scheduled_at
            job = self.queue.enqueue_at(
                task.scheduled_at,
                self.consume,
                task=task,
                on_success=self._scheduled_callback,
            )
            logger.info(
                f"[Task] Task {task.id} will be enqueued at {task.scheduled_at}"
            )
        elif task.scheduled_in and task.scheduled_time_unit:
            task.enqueued_at = timezone.now() + timedelta(**delay)
            job = self.queue.enqueue_in(
                timedelta(**{task.scheduled_time_unit.lower(): task.scheduled_in}),
                self.consume,
                task=task,
                on_success=self._scheduled_callback,
            )
            logger.info(
                f"[Task] Task {task.id} will be enqueued in {task.scheduled_in} {task.scheduled_time_unit}"
            )
        else:
            task.enqueued_at = timezone.now()
            job = self.queue.enqueue(
                self.consume, task=task, on_success=self._scheduled_callback
            )
            logger.info(f"[Task] Task {task.id} has been enqueued")
        task.rq_job_id = job.id
        task.save(update_fields=["enqueued_at", "rq_job_id"])
        return job

    @job("tasks-queue")
    def consume(self, task: Task) -> Task:
        if task.executions:
            task.executions.clear()
        if task.configuration:
            self._consume_tool_task(task)
        elif task.process:
            self._consume_process_task(task)
        return task

    def _consume_tool_task(self, task: Task) -> None:
        executions = self._calculate_executions(
            task.configuration.tool,
            [],
            task.target.target_ports,
            task.target.input_vulnerabilities,
            task.target.input_technologies,
            task.wordlists,
        )
        for parameters in executions or [{}]:
            execution = Execution.objects.create(
                task=task, configuration=task.configuration, group=1
            )
            self.executions_queue.enqueue(
                execution,
                [],
                parameters.get(1, []),
                parameters.get(2, []),
                parameters.get(3, []),
                parameters.get(4, []),
            )

    def _consume_process_task(self, task: Task) -> None:
        plan = []
        steps = (
            Step.objects.annotate(
                max_input=Max("tool__arguments__inputs__type__id"),
                max_output=Max("configuration__outputs__type__id"),
            )
            .filter(process=task.process)
            .order_by("configuration__stage", "max_output", "max_input")
        )
        for step in steps:
            item = {
                "step": step,
                "inputs": InputType.objects.filter(
                    inputs__argument__tool=step.configuration.tool
                ).distinct(),
                "outputs": InputType.objects.filter(
                    outputs__configuration=step.configuration
                ).distinct(),
                "dependencies": set(),
                "jobs": [],
                "group": 1,
            }
            if Intensity.objects.filter(
                tool=step.tool, value__lte=task.intensity
            ).exists():
                for job in plan:
                    for output in job.get("outputs"):
                        if output in item.get("inputs"):
                            item["group"] = max([item["group"], job["group"] + 1])
                            item["dependencies"].add(job)
                plan.append(item)
            else:
                Execution.objects.create(
                    task=task,
                    configuration=step.configuration,
                    group=1,
                    status=Status.SKIPPED,
                    skipped_reason=f"Tool {step.configuration.tool.name} can't be executed with intensity {task.intensity.value.value}",
                )
        for job in plan:
            executions = self._calculate_executions_from_task_parameters(
                step.configuration.tool,
                [],
                task.target.target_ports,
                task.target.input_vulnerabilities,
                task.target.input_technologies,
                task.wordlists,
            )
            for parameters in executions or [{}]:
                execution = Execution.objects.create(
                    task=task,
                    configuration=job.get("step").configuration,
                    group=job.get("group"),
                )
                job["jobs"].append(
                    self.executions_queue.enqueue(
                        execution,
                        parameters.get(0, []),
                        parameters.get(1, []),
                        parameters.get(2, []),
                        parameters.get(3, []),
                        parameters.get(4, []),
                        dependencies=sum(
                            [j.get("jobs") for j in job.get("dependencies")], []
                        ),
                    )
                )

    def _scheduled_callback(
        self, job: Any, connection: Any, result: Task, *args: Any, **kwargs: Any
    ) -> None:
        if result and result.repeat_in and result.repeat_time_unit:
            result.enqueued_at = result.enqueued_at + timedelta(
                **{result.repeat_time_unit.lower(): result.repeat_in}
            )
            job = self.queue.enqueue_at(
                result.enqueued_at,
                self.consume,
                task=result,
                on_success=self._scheduled_callback,
            )
            logger.info(f"[Task] Scheduled task {result.id} has been enqueued again")
            result.rq_job_id = job.id
            result.save(update_fields=["enqueued_at", "rq_job_id"])
