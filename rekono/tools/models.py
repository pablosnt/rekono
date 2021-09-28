from django.db import models

from tools.enums import IntensityRank, FindingType

# Create your models here.


class Tool(models.Model):

    class Stage(models.IntegerChoices):
        OSINT = 1
        ENUMERATION = 2
        VULNERABILITIES = 3
        SERVICES = 4
        EXPLOITATION = 5

    name = models.TextField(max_length=30)
    command = models.TextField(max_length=30, blank=True, null=True)
    stage = models.IntegerField(choices=Stage.choices)
    reference = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Intensity(models.Model):
    tool = models.ForeignKey(Tool, related_name='intensities', on_delete=models.CASCADE)
    argument = models.TextField(max_length=50, default='', blank=True)
    value = models.IntegerField(choices=IntensityRank.choices, default=IntensityRank.NORMAL)

    def __str__(self) -> str:
        return f'{self.tool.name} - {IntensityRank(self.value).name}'


class Configuration(models.Model):
    name = models.TextField(max_length=30)
    tool = models.ForeignKey(Tool, related_name='configurations', on_delete=models.CASCADE)
    arguments = models.TextField(max_length=250, blank=True, null=True)
    default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.tool.name} - {self.name}'


class Input(models.Model):

    class InputSelection(models.IntegerChoices):
        ALL = 1
        FOR_EACH = 2

    configuration = models.ForeignKey(
        Configuration,
        related_name='inputs',
        on_delete=models.CASCADE
    )
    name = models.TextField(max_length=20)
    type = models.IntegerField(choices=FindingType.choices)
    argument = models.TextField(max_length=50, blank=True, null=True)
    filter = models.TextField(max_length=250, blank=True, null=True)
    selection = models.IntegerField(choices=InputSelection.choices, default=InputSelection.FOR_EACH)
    required = models.BooleanField(default=False)

    def __str__(self) -> str:
        fk = self.configuration.__str__()
        return f'{fk} - {self.name}'


class Output(models.Model):
    configuration = models.ForeignKey(
        Configuration,
        related_name='outputs',
        on_delete=models.CASCADE
    )
    type = models.IntegerField(choices=FindingType.choices)

    def __str__(self) -> str:
        fk = self.configuration.__str__()
        return f'{fk} - {self.type}'
