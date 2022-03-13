from django.db import models
from processes.models import Step
from projects.models import Project
from tasks.enums import Status
from tasks.models import Task

# Create your models here.


class Execution(models.Model):
    '''Execution model.'''

    task = models.ForeignKey(Task, related_name='executions', on_delete=models.CASCADE)             # Related Task
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)          # Job Id in the executions queue
    # If it's a Process task, will be an execution for each Process step. If it's a Tool task, step is null
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, blank=True, null=True)
    extra_data_path = models.TextField(max_length=50, blank=True, null=True)    # Filepath with extra data
    output_file = models.TextField(max_length=50, blank=True, null=True)        # Tool output filepath
    output_plain = models.TextField(blank=True, null=True)                      # Tool output in plain text
    output_error = models.TextField(blank=True, null=True)                      # Tool errors
    status = models.TextField(max_length=10, choices=Status.choices, default=Status.REQUESTED)      # Execution status
    start = models.DateTimeField(blank=True, null=True)                         # Start date
    end = models.DateTimeField(blank=True, null=True)                           # End date
    reported_to_defectdojo = models.BooleanField(default=False)                 # Indicate if it has been imported yet

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        if self.step:
            return f'{self.task.__str__()} - {self.step.tool.name} - {self.step.configuration.name}'
        else:
            return self.task.__str__()

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.task.target.project
