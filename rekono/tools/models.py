from typing import Any

from django.db import models
from input_types.models import InputType
from likes.models import LikeBase
from tools.enums import IntensityRank, Stage

# Create your models here.


class Tool(LikeBase):
    name = models.TextField(max_length=30, unique=True)
    command = models.TextField(max_length=30, blank=True, null=True)
    output_format = models.TextField(max_length=5, blank=True, null=True)
    defectdojo_scan_type = models.TextField(max_length=50, blank=True, null=True)
    stage = models.IntegerField(choices=Stage.choices)
    reference = models.TextField(max_length=250, blank=True, null=True)
    icon = models.TextField(max_length=250, blank=True, null=True)

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


class Argument(models.Model):
    tool = models.ForeignKey(Tool, related_name='arguments', on_delete=models.CASCADE)
    name = models.TextField(max_length=20)
    argument = models.TextField(max_length=50, default='', blank=True)
    required = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['tool', 'name'], name='unique argument')
        ]

    def __str__(self) -> str:
        return f'{self.tool.__str__()} - {self.name}'

    def get_project(self) -> Any:
        return None


class Input(models.Model):
    argument = models.ForeignKey(Argument, related_name='inputs', on_delete=models.CASCADE)
    type = models.ForeignKey(InputType, related_name='inputs', on_delete=models.CASCADE)
    filter = models.TextField(max_length=250, blank=True, null=True)
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['argument', 'order'], name='unique input')
        ]
    
    def __str__(self) -> str:
        return f'{self.argument.__str__()} - {self.type.__str__()}'

    def get_project(self) -> Any:
        return None


class Output(models.Model):
    configuration = models.ForeignKey(
        Configuration,
        related_name='outputs',
        on_delete=models.CASCADE
    )
    type = models.ForeignKey(InputType, related_name='outputs', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['configuration', 'type'], name='unique output')
        ]

    def __str__(self) -> str:
        return f'{self.configuration.__str__()} - {self.type.__str__()}'

    def get_project(self) -> Any:
        return None
