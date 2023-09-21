from django.db import models
from executions.enums import Status
from processes.models import Process
from rekono.settings import AUTH_USER_MODEL
from security.utils.input_validator import TimeValidator
from targets.models import Target
from tasks.enums import TimeUnit
from tools.enums import Intensity
from tools.models import Configuration
from wordlists.models import Wordlist

# Create your models here.


class Task(models.Model):
    """Task model."""

    # Job Id in the tasks queue
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    target = models.ForeignKey(Target, related_name="tasks", on_delete=models.CASCADE)
    process = models.ForeignKey(
        Process, blank=True, null=True, on_delete=models.SET_NULL
    )
    configuration = models.ForeignKey(
        Configuration, on_delete=models.SET_NULL, blank=True, null=True
    )
    intensity = models.IntegerField(choices=Intensity.choices, default=Intensity.NORMAL)
    executor = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    # Date when the task will be executed
    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        validators=[TimeValidator("scheduled_at").future_datetime],
    )
    # Amount of time before task execution
    scheduled_in = models.IntegerField(
        blank=True,
        null=True,
        validators=[TimeValidator("scheduled_in").time_amount],
    )
    # Time unit to apply to the 'sheduled in' value
    scheduled_time_unit = models.TextField(
        max_length=10, choices=TimeUnit.choices, blank=True, null=True
    )
    # Amount of time to wait until repeating the task execution
    repeat_in = models.IntegerField(
        blank=True,
        null=True,
        validators=[TimeValidator("repeat_in").time_amount],
    )
    # Time unit to apply to the 'repeat in' value
    repeat_time_unit = models.TextField(
        max_length=10, choices=TimeUnit.choices, blank=True, null=True
    )
    creation = models.DateTimeField(auto_now_add=True)
    # Date at task got enqueued
    enqueued_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    wordlists = models.ManyToManyField(Wordlist, related_name="wordlists", blank=True)

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        value = f"{self.target.__str__()} - "
        if self.process:
            value += self.process.__str__()
        elif self.configuration:
            value += self.configuration.__str__()
        return value

    @classmethod
    def get_project_field(cls) -> str:
        return "target__project"
