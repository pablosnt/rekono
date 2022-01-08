from typing import Any

from django.db import models
from inputs.base import BaseInput
from inputs.enums import InputKeyword
from inputs.utils import get_url
from projects.models import Project
from targets.enums import TargetType
from tools.models import Input

# Create your models here.


class Target(models.Model, BaseInput):
    project = models.ForeignKey(
        Project,
        related_name='targets',
        on_delete=models.CASCADE
    )
    target = models.TextField(max_length=100)
    type = models.TextField(max_length=10, choices=TargetType.choices)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['project', 'target'], name='unique target')
        ]

    def filter(self, input: Input) -> bool:
        try:
            return TargetType[input.filter] == self.type
        except KeyError:
            return True
    
    def parse(self, accumulated: dict = {}) -> dict:
        return {
            InputKeyword.TARGET.name.lower(): self.target,
            InputKeyword.HOST.name.lower(): self.target,
            InputKeyword.URL.name.lower(): get_url(self.target)
        }

    def __str__(self) -> str:
        return self.target

    def get_project(self) -> Any:
        return self.project


class TargetPort(models.Model, BaseInput):
    target = models.ForeignKey(
        Target,
        related_name='target_ports',
        on_delete=models.CASCADE
    )
    port = models.IntegerField()

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['target', 'port'], name='unique target port')
        ]

    def parse(self, accumulated: dict = {}) -> dict:
        output = {
            InputKeyword.TARGET.name.lower(): self.target.target,
            InputKeyword.HOST.name.lower(): self.target.target,
            InputKeyword.PORT.name.lower(): self.port,
            InputKeyword.PORTS.name.lower(): [self.port],
            InputKeyword.URL.name.lower(): get_url(self.target.target, self.port)
        }
        if accumulated and InputKeyword.PORTS.name.lower() in accumulated:
            output[InputKeyword.PORTS.name.lower()] = accumulated[InputKeyword.PORTS.name.lower()]
            output[InputKeyword.PORTS.name.lower()].append(self.port)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ','.join([str(port) for port in output[InputKeyword.PORTS.name.lower()]])    # noqa: E501
        return output

    def __str__(self) -> str:
        return f'{self.target.target} - {self.port}'

    def get_project(self) -> Any:
        return self.target.project


class TargetEndpoint(models.Model, BaseInput):
    target_port = models.ForeignKey(
        TargetPort,
        related_name='target_endpoints',
        on_delete=models.CASCADE
    )
    endpoint = models.TextField(max_length=500)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['target_port', 'endpoint'],
                name='unique target endpoint'
            )
        ]
    
    def parse(self, accumulated: dict = {}) -> dict:
        output = self.target_port.parse()
        output[InputKeyword.URL.name.lower()] = get_url(
            self.target_port.target.target,
            self.target_port.port,
            self.endpoint
        )
        output[InputKeyword.ENDPOINT.name.lower()] = self.endpoint
        return output
    
    def __str__(self) -> str:
        return f'{self.target_port.__str__()} - {self.endpoint}'

    def get_project(self) -> Any:
        return self.target_port.target.project
