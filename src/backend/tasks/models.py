from django.conf import settings
from django.db import models
from processes.models import Process
from projects.models import Project
from resources.models import Wordlist
from security.input_validation import validate_time_amount
from targets.models import Target
from tools.enums import IntensityRank
from tools.models import Configuration, Tool

from tasks.enums import Status, TimeUnit

# Create your models here.


class Task(models.Model):
    '''Task model.'''

    rq_job_id = models.TextField(max_length=50, blank=True, null=True)          # Job Id in the tasks queue
    target = models.ForeignKey(Target, related_name='tasks', on_delete=models.CASCADE)              # Related target
    process = models.ForeignKey(Process, blank=True, null=True, on_delete=models.SET_NULL)  # Process to be executed
    tool = models.ForeignKey(Tool, blank=True, null=True, on_delete=models.SET_NULL)        # Tool to be executed
    # Configuration to be applied (only for Tool tasks)
    configuration = models.ForeignKey(Configuration, on_delete=models.SET_NULL, blank=True, null=True)
    # Intensity to be applied in the tool executions
    intensity = models.IntegerField(choices=IntensityRank.choices, default=IntensityRank.NORMAL)
    # User that has requested the task
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.TextField(max_length=10, choices=Status.choices, default=Status.REQUESTED)  # Task status
    scheduled_at = models.DateTimeField(blank=True, null=True)                  # Date when the task will be executed
    # Amount of time before task execution
    scheduled_in = models.IntegerField(blank=True, null=True, validators=[validate_time_amount])
    # Time unit to apply to the 'sheduled in' value
    scheduled_time_unit = models.TextField(max_length=10, choices=TimeUnit.choices, blank=True, null=True)
    # Amount of time before repeat task execution
    repeat_in = models.IntegerField(blank=True, null=True, validators=[validate_time_amount])
    # Time unit to apply to the 'repeat in' value
    repeat_time_unit = models.TextField(max_length=10, choices=TimeUnit.choices, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)                          # Creation date
    enqueued_at = models.DateTimeField(blank=True, null=True)                   # Date at task got enqueued
    start = models.DateTimeField(blank=True, null=True)                         # Task execution start date
    end = models.DateTimeField(blank=True, null=True)                           # Task execution end date
    wordlists = models.ManyToManyField(Wordlist, related_name='wordlists', blank=True)  # Wordlists applied

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        value = f'{self.target.project.name} - {self.target.target} - '
        if self.process:
            value += self.process.name
        elif self.tool:
            value += self.tool.name
            if self.configuration:
                value += f' - {self.configuration.name}'
        return value

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.target.project
