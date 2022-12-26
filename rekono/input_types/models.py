from typing import Union

from django.apps import apps
from django.db import models

from input_types.base import BaseInput
from input_types.enums import InputTypeNames

# Create your models here.


class InputType(models.Model):
    '''Input type model, related to each object type that can be included in a tool argument.'''

    name = models.TextField(max_length=15, choices=InputTypeNames.choices)      # Input type name
    # Related model name in 'app.Model' format. It can be a reference to a Finding
    model = models.TextField(max_length=30, null=True, blank=True)
    # Related callback model name in 'app.Model' format. It will be used when 'model' is not available
    callback_model = models.TextField(max_length=15, null=True, blank=True)
    # Indicate if the input type should be included to calculate relations between models and executions
    regular = models.BooleanField(default=True)

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.name

    def get_class_from_reference(self, reference: str) -> BaseInput:
        '''Get model from string reference.

        Args:
            reference (str): Reference to model

        Returns:
            Union[BaseInput, None]: Model class related to reference
        '''
        app_label, model_name = reference.split('.', 1)                         # Get model attributes from reference
        return apps.get_model(app_label=app_label, model_name=model_name)

    def get_model_class(self) -> Union[BaseInput, None]:
        '''Get related model from 'model' reference.

        Returns:
            BaseInput: Related model of the input type
        '''
        return self.get_class_from_reference(self.model) if self.model else None

    def get_callback_model_class(self) -> Union[BaseInput, None]:
        '''Get callback model from 'callback_model' reference.

        Returns:
            BaseInput: Callback model of the input type
        '''
        return self.get_class_from_reference(self.callback_model) if self.callback_model else None
