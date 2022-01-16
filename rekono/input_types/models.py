from typing import Any

from django.apps import apps
from django.db import models
from input_types.base import BaseInput
from input_types.enums import InputTypeNames

# Create your models here.


class InputType(models.Model):
    '''Input type model, related to each object type that can be included in a tool argument.'''

    name = models.TextField(max_length=15, choices=InputTypeNames.choices)      # Input type name
    # Related model name in 'app.Model' format. It can be a reference to a Finding or a Resource
    related_model = models.TextField(max_length=30)
    # Related target model name in 'Model' format. It will be used when 'related_model' is not available.
    callback_target = models.TextField(max_length=15, null=True, blank=True)

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.name

    def get_project(self) -> Any:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return None

    def get_related_model_class(self) -> BaseInput:
        '''Get related model from 'related_model' reference.

        Returns:
            BaseInput: Related model of the input type
        '''
        app_label, model_name = self.related_model.split('.', 1)                # Parse 'related_model' field
        return apps.get_model(app_label=app_label, model_name=model_name)

    def get_callback_target_class(self) -> BaseInput:
        '''Get callback target model from 'callback_target' reference.

        Returns:
            BaseInput: Target model of the input type
        '''
        return apps.get_model(app_label='targets', model_name=self.callback_target)
