from typing import Any

from django.conf import settings
from django.db import models
from processes.models import Process
from resources.models import Wordlist
from targets.models import Target
from tasks.enums import Status, TimeUnit
from tools.enums import IntensityRank
from tools.models import Configuration, Tool

# Create your models here.


class Task(models.Model):
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    target = models.ForeignKey(Target, related_name='tasks', on_delete=models.CASCADE)
    process = models.ForeignKey(Process, blank=True, null=True, on_delete=models.SET_NULL)
    tool = models.ForeignKey(Tool, blank=True, null=True, on_delete=models.SET_NULL)
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    intensity = models.IntegerField(choices=IntensityRank.choices, default=IntensityRank.NORMAL)
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    status = models.TextField(max_length=10, choices=Status.choices, default=Status.REQUESTED)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    scheduled_in = models.IntegerField(blank=True, null=True)
    scheduled_time_unit = models.TextField(
        max_length=10,
        choices=TimeUnit.choices,
        blank=True,
        null=True
    )
    repeat_in = models.IntegerField(blank=True, null=True)
    repeat_time_unit = models.TextField(
        max_length=10,
        choices=TimeUnit.choices,
        blank=True,
        null=True
    )
    creation = models.DateTimeField(auto_now_add=True)
    enqueued_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    wordlists = models.ManyToManyField(Wordlist, related_name='wordlists', blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        value = f'{self.target.project.name} - {self.target.target} - '
        if self.process:
            value += self.process.name
        elif self.tool:
            value += self.tool.name
            if self.configuration:
                value += f' - {self.configuration.name}'
        return value

    def get_project(self) -> Any:
        return self.target.project
