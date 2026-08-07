"""Model of the executions, which are the runs of one tool against a target."""

import logging
from typing import Any

from django.db import models
from django.utils import timezone

from executions.enums import Status
from framework.models import BaseModel
from tasks.models import Task
from tools.models import Configuration


class Execution(BaseModel):
    """Run of one tool configuration, planned by a task.

    An execution can also be created directly as skipped, when its tool is never
    going to run because the target was denied or the tool doesn't support the
    intensity of the task, so the history of a task shows every step of it.

    Attributes:
        task: Task that planned this execution.
        rq_job_id: Identifier of the job in the executions queue, needed to cancel
          or stop it.
        configuration: Tool configuration that the execution runs.
        output_file: Path of the file where the tool wrote its report.
        output_plain: Output that the tool wrote in the standard output.
        executed_command: Command that was executed, with the secrets removed.
        skipped_reason: Why the execution never ran, for the skipped ones.
        status: Current status of the execution.
        enqueued_at: Moment when the execution was enqueued.
        start: Moment when the tool started.
        end: Moment when the execution reached a final status.
        hash: Hash of the execution environment, used to deduplicate findings.
        defectdojo_test_id: Test that this execution created in DefectDojo, if the
          project is synchronized with it.
    """

    task = models.ForeignKey(Task, related_name="executions", on_delete=models.CASCADE, blank=True, null=True)
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    configuration = models.ForeignKey(Configuration, on_delete=models.SET_NULL, blank=True, null=True)
    output_file = models.TextField(max_length=50, blank=True, null=True)
    output_plain = models.TextField(blank=True, null=True)
    executed_command = models.TextField(blank=True, null=True)
    skipped_reason = models.TextField(blank=True, null=True)
    status = models.TextField(max_length=10, choices=Status.choices, default=Status.REQUESTED)
    enqueued_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    hash = models.TextField(max_length=128, blank=True, null=True)
    defectdojo_test_id = models.IntegerField(blank=True, null=True)

    _project_field = "task__target__project"

    def __str__(self) -> str:
        """Return the task, adding the configuration when the task runs a process.

        The representation of a task that runs one configuration already names it,
        so it isn't repeated here.
        """
        return f"{self.task.__str__()}{f' - {self.configuration.__str__()}' if self.task.process else ''}"

    def started(self) -> None:
        """Mark the execution as RUNNING and anchor the parent task start.

        Sets the status and the start timestamp, then pulls the parent task start
        back to the earliest start among its executions, so parallel executions
        can never leave the task starting later than one of its own executions.
        """
        self.status = Status.RUNNING
        self.start = timezone.now()
        self.save(update_fields=["start", "status"])
        earliest = Execution.objects.filter(task=self.task, start__isnull=False).order_by("start").first()
        if earliest and earliest.id == self.id:
            self.task.start = earliest.start
            self.task.save(update_fields=["start"])

    def skipped(self, skipped_reason: str) -> None:
        """Mark the execution as SKIPPED with the reason it was not run.

        Called after started() has already put the execution into RUNNING, when
        the tool is missing or its arguments cannot be built. The execution
        keeps the start timestamp it was given even though the tool itself
        never actually runs.

        Args:
            skipped_reason: Reason why the execution was skipped, which is shown to
              the users.
        """
        self.logger.error(f"[Tool] {self.configuration.tool.name} execution was skipped due to '{skipped_reason}'")
        self.finish(Status.SKIPPED, skipped_reason=skipped_reason)

    def error(self) -> None:
        """Mark the execution as ERROR after the tool failed or crashed."""
        self.logger.error(f"[Tool] {self.configuration.tool.name} execution finished with errors")
        self.finish(Status.ERROR)

    def completed(self, hash: str) -> None:
        """Mark the execution as COMPLETED and store its deduplication hash.

        Args:
            hash: Hash computed by the executor from the run environment and
              arguments, used later to deduplicate findings across executions.
        """
        self.logger.info(f"[Tool] {self.configuration.tool.name} execution has been completed")
        self.finish(Status.COMPLETED, hash=hash)

    def finish(self, status: Status, **fields: Any) -> None:
        """Apply a terminal status to the execution and settle the parent task end.

        Sets the terminal status and the end timestamp, together with any extra model
        fields, persists them, and then anchors the parent task end once none of its
        executions remain pending. Shared by the executor lifecycle, the orphaned
        execution reconciliation and the job failure callback so every terminal
        transition behaves the same way.

        Args:
            status: Terminal status to apply to the execution.
            **fields: Extra model fields to persist alongside status and end
              (e.g. ``skipped_reason`` or ``hash``).
        """
        self.status = status
        self.end = timezone.now()
        for field, value in fields.items():
            setattr(self, field, value)
        self.save(update_fields=["status", "end", *fields.keys()])
        if self.task and not Execution.objects.filter(task=self.task, status__in=Status.in_progress()).exists():
            latest = (
                Execution.objects.filter(task=self.task, end__isnull=False, status__in=Status.finished())
                .order_by("-end")
                .first()
            )
            if latest and latest.id == self.id:
                self.task.end = self.end
                self.task.save(update_fields=["end"])
                logging.getLogger().info(f"[Task] Task {self.task.id} has finished")
