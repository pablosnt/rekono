from typing import Any

from django.apps import apps
from django.db import models
from inputs.enums import InputTypeNames

from rekono.inputs.base import BaseInput

# Create your models here.


class InputType(models.Model):
    name = models.TextField(max_length=15, choices=InputTypeNames.choices)
    related_model = models.TextField(max_length=30)
    callback_target = models.TextField(max_length=15, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def get_project(self) -> Any:
        return None

    def get_related_model_class(self) -> BaseInput:
        app_label, model_name = self.related_model.split('.', 1)
        return apps.get_model(app_label=app_label, model_name=model_name)
    
    def get_callback_target_class(self) -> BaseInput:
        return apps.get_model(app_label='targets', model_name=self.callback_target)
