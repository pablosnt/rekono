from typing import Any

from django.conf import settings
from django.db import models
from executions.enums import ParameterKey, Status, TimeUnit
from processes.models import Process, Step
from projects.models import Target
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
    status = models.IntegerField(choices=Status.choices, default=Status.REQUESTED)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    scheduled_in = models.IntegerField(blank=True, null=True)
    scheduled_time_unit = models.IntegerField(choices=TimeUnit.choices, blank=True, null=True)
    repeat_in = models.IntegerField(blank=True, null=True)
    repeat_time_unit = models.IntegerField(choices=TimeUnit.choices, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

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


class Parameter(models.Model):
    task = models.ForeignKey(Task, related_name='parameters', on_delete=models.CASCADE)
    key = models.IntegerField(choices=ParameterKey.choices)
    value = models.TextField(max_length=250)

    def get_project(self) -> Any:
        return self.task.target.project


class Execution(models.Model):
    task = models.ForeignKey(Task, related_name='executions', on_delete=models.CASCADE)
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    rq_job_pid = models.IntegerField(blank=True, null=True)
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, blank=True, null=True)
    output_file = models.TextField(max_length=50, blank=True, null=True)
    output_plain = models.TextField(blank=True, null=True)
    output_error = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.REQUESTED)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        if self.step:
            req = self.task.__str__()
            return f'{req} - {self.step.tool.name} - {self.step.configuration.name}'
        else:
            return self.task.__str__()

    def get_project(self) -> Any:
        return self.task.target.project
