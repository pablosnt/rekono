from django.db import models
from projects.models import Project
from tasks.enums import Status
from tasks.models import Task
from tools.models import Configuration, Tool

# Create your models here.


class Execution(models.Model):
    '''Execution model.'''

    task = models.ForeignKey(Task, related_name='executions', on_delete=models.CASCADE)             # Related Task
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)          # Job Id in the executions queue
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)                    # Tool
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE, blank=True, null=True)   # Configuration
    extra_data_path = models.TextField(max_length=50, blank=True, null=True)    # Filepath with extra data
    output_file = models.TextField(max_length=50, blank=True, null=True)        # Tool output filepath
    output_plain = models.TextField(blank=True, null=True)                      # Tool output in plain text
    output_error = models.TextField(blank=True, null=True)                      # Tool errors
    status = models.TextField(max_length=10, choices=Status.choices, default=Status.REQUESTED)      # Execution status
    start = models.DateTimeField(blank=True, null=True)                         # Start date
    end = models.DateTimeField(blank=True, null=True)                           # End date
    imported_in_defectdojo = models.BooleanField(default=False)                 # Indicate if it has been imported yet

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return (
            f'{self.task.target.project.name} - {self.task.target.target} - '
            f'{self.tool.name} - {self.configuration.name}'
        )

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.task.target.project
