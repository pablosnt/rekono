from typing import Any

from django.db import models
from processes.models import Step
from tasks.enums import Status
from tasks.models import Task

# Create your models here.


class Execution(models.Model):
    task = models.ForeignKey(Task, related_name='executions', on_delete=models.CASCADE)
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    rq_job_pid = models.IntegerField(blank=True, null=True)
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, blank=True, null=True)
    output_file = models.TextField(max_length=50, blank=True, null=True)
    output_plain = models.TextField(blank=True, null=True)
    output_error = models.TextField(blank=True, null=True)
    status = models.TextField(max_length=10, choices=Status.choices, default=Status.REQUESTED)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        if self.step:
            req = self.task.__str__()
            return f'{req} - {self.step.tool.name} - {self.step.configuration.name}'
        else:
            return self.task.__str__()

    def get_project(self) -> Any:
        return self.task.target.project
