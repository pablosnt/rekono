from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseModel
from parameters.models import InputTechnology, InputVulnerability
from processes.models import Process
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import FutureDatetimeValidator
from targets.models import Target
from tasks.enums import TimeUnit
from tools.enums import Intensity
from tools.models import Configuration
from wordlists.models import Wordlist

# Create your models here.


class Task(BaseModel):
    """Task model."""

    # Job Id in the tasks queue
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    target = models.ForeignKey(Target, related_name="tasks", on_delete=models.CASCADE)
    process = models.ForeignKey(Process, blank=True, null=True, on_delete=models.SET_NULL)
    configuration = models.ForeignKey(Configuration, on_delete=models.SET_NULL, blank=True, null=True)
    intensity = models.IntegerField(choices=Intensity.choices, default=Intensity.NORMAL)
    executor = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    # Date when the task will be executed
    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        validators=[FutureDatetimeValidator(code="scheduled_at")],
    )
    # Amount of time to wait until repeating the task execution
    repeat_in = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
    )
    # Time unit to apply to the 'repeat in' value
    repeat_time_unit = models.TextField(max_length=10, choices=TimeUnit.choices, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)
    # Date at task got enqueued
    enqueued_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    wordlists = models.ManyToManyField(Wordlist, related_name="tasks", blank=True)
    input_technologies = models.ManyToManyField(InputTechnology, related_name="tasks", blank=True)
    input_vulnerabilities = models.ManyToManyField(InputVulnerability, related_name="tasks", blank=True)

    project_field = "target__project"

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.target.__str__()} - {(self.process or self.configuration).__str__()}"
