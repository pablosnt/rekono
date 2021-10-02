from django.conf import settings
from django.db import models
from tools.models import Tool, Configuration

# Create your models here.


class Process(models.Model):
    name = models.TextField(max_length=30)
    description = models.TextField(max_length=250)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Step(models.Model):

    class Priority(models.IntegerChoices):
        ASAP = 1
        STANDARD = 2
        LAST = 3

    process = models.ForeignKey(Process, related_name='steps', on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.STANDARD)
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self) -> str:
        return self.process.__str__() + ' - ' + self.configuration.__str__()
