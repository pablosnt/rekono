"""Execution models for Rekono.

This module defines the Execution model which tracks the lifecycle of security
tool executions, including status tracking, timing information, and result
management for security testing workflows.
"""

from django.db import models

from executions.enums import Status
from framework.models import BaseModel
from tasks.models import Task
from tools.models import Configuration


class Execution(BaseModel):
    """Execution model for tracking security tool runs.

    This model represents a single execution of a security tool within
    the Rekono platform. It tracks the complete lifecycle from queuing
    to completion, including status updates, timing information, and
    result management.

    Attributes:
        task (ForeignKey): The task that triggered this execution.
        rq_job_id (TextField): Redis Queue job identifier for background processing.
        configuration (ForeignKey): The tool configuration used for this execution.
        output_file (TextField): Path to the execution output file.
        output_plain (TextField): Plain text output from the tool execution.
        skipped_reason (TextField): Reason why the execution was skipped.
        status (TextField): Current status of the execution.
        enqueued_at (DateTimeField): When the execution was queued.
        start (DateTimeField): When the execution started.
        end (DateTimeField): When the execution completed.
        hash (TextField): Hash of the execution for deduplication.
        defectdojo_test_id (IntegerField): ID of the test in DefectDojo.
    """

    task = models.ForeignKey(Task, related_name="executions", on_delete=models.CASCADE, blank=True, null=True)
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE, blank=True, null=True)
    output_file = models.TextField(max_length=50, blank=True, null=True)
    output_plain = models.TextField(blank=True, null=True)
    skipped_reason = models.TextField(blank=True, null=True)
    status = models.TextField(max_length=10, choices=Status.choices, default=Status.REQUESTED)
    enqueued_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    hash = models.TextField(max_length=128, blank=True, null=True)
    defectdojo_test_id = models.IntegerField(blank=True, null=True)

    _project_field = "task__target__project"

    def __str__(self) -> str:
        """String representation of the execution record.

        Returns:
            str: String in format "task - configuration" or just "task" if no
                process is associated.
        """
        return f"{self.task.__str__()}{f' - {self.configuration.__str__()}' if self.task.process else ''}"
