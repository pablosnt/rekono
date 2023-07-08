from django.conf import settings
from django.db import models
from likes.models import LikeBase
from security.input_validation import (validate_name, validate_number,
                                       validate_text)
from taggit.managers import TaggableManager
from tools.models import Configuration, Tool

# Create your models here.


class Process(LikeBase):
    '''Process model.'''

    name = models.TextField(max_length=100, unique=True, validators=[validate_name])                # Process name
    description = models.TextField(max_length=300, validators=[validate_text])  # Process description
    # User that created the process
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    tags = TaggableManager()                                                    # Process tags

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.name


class Step(models.Model):
    '''Process model.'''

    process = models.ForeignKey(Process, related_name='steps', on_delete=models.CASCADE)    # Associated process
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)                    # Tool
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE, blank=True, null=True)   # Configuration
    # Priority value. Steps with greater priority will be executed before other of same process and with same stage
    priority = models.IntegerField(default=1, validators=[validate_number])

    class Meta:
        '''Model metadata.'''

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
