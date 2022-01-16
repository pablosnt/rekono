from typing import Any

from django.conf import settings
from django.db import models
from taggit.managers import TaggableManager

# Create your models here.


class Project(models.Model):
    '''Project model.'''

    name = models.TextField(max_length=50, unique=True)                         # Project name
    description = models.TextField(max_length=250)                              # Project description
    defectdojo_product_id = models.IntegerField(blank=True, null=True)          # Related product Id in Defect-Dojo
    owner = models.ForeignKey(                                                  # User that created the project
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    # Relation with all users that belong to the project
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='members', blank=True)
    tags = TaggableManager()                                                    # Project tags

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
        return self
