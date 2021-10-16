from django.db import models
from typing import Any
from projects.models import Project
from targets.enums import TargetType

# Create your models here.


class Target(models.Model):
    project = models.ForeignKey(
        Project,
        related_name='targets',
        on_delete=models.CASCADE
    )
    target = models.TextField(max_length=100)
    type = models.IntegerField(choices=TargetType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'target'], name='unique target')
        ]

    def __str__(self) -> str:
        return self.target

    def get_project(self) -> Any:
        return self.project


class TargetPort(models.Model):
    target = models.ForeignKey(
        Target,
        related_name='target_ports',
        on_delete=models.CASCADE
    )
    port = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['target', 'port'], name='unique target port')
        ]

    def __str__(self) -> str:
        return f'{self.target.target} - {self.port}'

    def get_project(self) -> Any:
        return self.target.project
