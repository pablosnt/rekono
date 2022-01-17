from typing import Any

from django.conf import settings
from django.db import models
from likes.models import LikeBase
from taggit.managers import TaggableManager
from tools.models import Configuration, Tool

# Create your models here.


class Process(LikeBase):
    '''Process model.'''

    name = models.TextField(max_length=30, unique=True)                         # Process name
    description = models.TextField(max_length=250)                              # Process description
    # User that created the process
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    tags = TaggableManager()                                                    # Process tags

    class Meta:
        '''Model metadata.'''

        ordering = ['-id']                                                      # Default ordering for pagination

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.name

    def get_project(self) -> Any:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Any: Related project entity
        '''
        return None


class Step(models.Model):
    '''Process model.'''

    process = models.ForeignKey(Process, related_name='steps', on_delete=models.CASCADE)    # Associated process
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)                    # Tool
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE, blank=True, null=True)   # Configuration
    # Priority value. Steps with greater priority will be executed before other of same process and with same tool stage
    priority = models.IntegerField(default=1)

    class Meta:
        '''Model metadata.'''

        ordering = ['-id']                                                      # Default ordering for pagination
        constraints = [
            # Unique constraint by: Process, Tool and Configuration
            models.UniqueConstraint(fields=['process', 'tool', 'configuration'], name='unique step')
        ]

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.process.__str__()} - {self.configuration.__str__()}'

    def get_project(self) -> Any:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return None
