from django.db import models
from executions.enums import Status
from tasks.models import Task
from tools.models import Configuration

# Create your models here.


class Execution(models.Model):
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
        if self.task.process:
            return f"{self.task.__str__()} - {self.configuration.__str__()}"
        else:
            return self.task.__str__()

    @classmethod
    def get_project_field(cls) -> str:
        return "task__target__project"