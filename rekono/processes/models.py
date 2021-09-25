from django.db import models
from django.contrib.auth.models import User
from tools.models import Tool, Configuration

# Create your models here.


class Process(models.Model):
    name = models.TextField(max_length=30)
    description = models.TextField(max_length=250)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Step(models.Model):

    class Priority(models.IntegerChoices):
        LOW = 1
        MEDIUM = 2
        HIGH = 3

    process = models.ForeignKey(Process, related_name='steps', on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self) -> str:
        return self.process.__str__() + ' - ' + self.configuration.__str__()
