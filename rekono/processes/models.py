from typing import Any

from django.conf import settings
from django.db import models
from tools.models import Configuration, Tool

# Create your models here.


class Process(models.Model):
    name = models.TextField(max_length=30, unique=True)
    description = models.TextField(max_length=250)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name

    def get_project(self) -> Any:
        return None


class Step(models.Model):
    process = models.ForeignKey(Process, related_name='steps', on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    priority = models.IntegerField()
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['process', 'tool', 'configuration'], name='unique step')
        ]

    def __str__(self) -> str:
        return self.process.__str__() + ' - ' + self.configuration.__str__()

    def get_project(self) -> Any:
        return None
