from typing import Any

from django.db import models
from tools.enums import FindingType, InputSelection, IntensityRank, Stage

# Create your models here.


class Tool(models.Model):
    name = models.TextField(max_length=30, unique=True)
    command = models.TextField(max_length=30, blank=True, null=True)
    output_format = models.TextField(max_length=5, blank=True, null=True)
    defectdojo_scan_type = models.TextField(max_length=50, blank=True, null=True)
    stage = models.IntegerField(choices=Stage.choices)
    reference = models.TextField(max_length=250, blank=True, null=True)
    icon = models.TextField(max_length=250, blank=True, null=True)
    for_each_target_port = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name

    def get_project(self) -> Any:
        return None


class Intensity(models.Model):
    tool = models.ForeignKey(Tool, related_name='intensities', on_delete=models.CASCADE)
    argument = models.TextField(max_length=50, default='', blank=True)
    value = models.IntegerField(choices=IntensityRank.choices, default=IntensityRank.NORMAL)

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.tool.name} - {IntensityRank(self.value).name}'

    def get_project(self) -> Any:
        return None


class Configuration(models.Model):
    name = models.TextField(max_length=30)
    tool = models.ForeignKey(Tool, related_name='configurations', on_delete=models.CASCADE)
    arguments = models.TextField(max_length=250, default='', blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['tool', 'name'], name='unique configuration')
        ]

    def __str__(self) -> str:
        return f'{self.tool.name} - {self.name}'

    def get_project(self) -> Any:
        return None


class Input(models.Model):
    configuration = models.ForeignKey(
        Configuration,
        related_name='inputs',
        on_delete=models.CASCADE
    )
    name = models.TextField(max_length=20)
    type = models.TextField(max_length=15, choices=FindingType.choices)
    argument = models.TextField(max_length=50, default='', blank=True)
    filter = models.TextField(max_length=250, blank=True, null=True)
    selection = models.TextField(
        max_length=10,
        choices=InputSelection.choices,
        default=InputSelection.FOR_EACH
    )
    required = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['configuration', 'type'], name='unique input')
        ]

    def __str__(self) -> str:
        fk = self.configuration.__str__()
        return f'{fk} - {self.name}'

    def get_project(self) -> Any:
        return None


class Output(models.Model):
    configuration = models.ForeignKey(
        Configuration,
        related_name='outputs',
        on_delete=models.CASCADE
    )
    type = models.TextField(max_length=15, choices=FindingType.choices)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['configuration', 'type'], name='unique output')
        ]

    def __str__(self) -> str:
        fk = self.configuration.__str__()
        return f'{fk} - {self.type}'

    def get_project(self) -> Any:
        return None
