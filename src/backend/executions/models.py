from django.db import models
from executions.enums import Status
from framework.models import BaseModel
from tasks.models import Task
from tools.models import Configuration

# Create your models here.


class Execution(BaseModel):
    """Execution model."""

    task = models.ForeignKey(
        Task, related_name="executions", on_delete=models.CASCADE, blank=True, null=True
    )
    group = models.IntegerField(default=1)
    # Job Id in the executions queue
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    configuration = models.ForeignKey(
        Configuration, on_delete=models.CASCADE, blank=True, null=True
    )
    output_file = models.TextField(max_length=50, blank=True, null=True)
    output_plain = models.TextField(blank=True, null=True)
    output_error = models.TextField(blank=True, null=True)
    skipped_reason = models.TextField(blank=True, null=True)
    status = models.TextField(
        max_length=10, choices=Status.choices, default=Status.REQUESTED
    )
    enqueued_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    defect_dojo_test_id = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.task.__str__()}{f' - {self.configuration.__str__()}' if self.task.process else ''}"

    @classmethod
    def get_project_field(cls) -> str:
        return "task__target__project"
