from typing import List, Self, Union

from django.apps import apps
from django.db import models
from framework.models import BaseInput, BaseModel
from input_types.enums import InputTypeName

# Create your models here.


class InputType(BaseModel):
    """Input type model, related to each object type that can be included in a tool argument."""

    name = models.TextField(max_length=15, choices=InputTypeName.choices)
    # Related model name in 'app.Model' format. It can be a reference to a Finding
    model = models.TextField(max_length=30, null=True, blank=True)
    # Related callback model name in 'app.Model' format. It will be used when 'model' is not available
    callback_model = models.TextField(max_length=15, null=True, blank=True)
    # Indicate if the input type should be included to calculate relations between models and executions
    relationships = models.BooleanField(default=True)

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.name

    def _get_class_from_reference(self, reference: str) -> BaseInput:
        """Get model from string reference.

        Args:
            reference (str): Reference to model

        Returns:
            Union[BaseInput, None]: Model class related to reference
        """
        if not reference:
            return None
        app_label, model_name = reference.split(
            ".", 1
        )  # Get model attributes from reference
        return apps.get_model(app_label=app_label, model_name=model_name)

    def get_model_class(self) -> Union[BaseInput, None]:
        """Get related model from 'model' reference.

        Returns:
            BaseInput: Related model of the input type
        """
        return self._get_class_from_reference(self.model)

    def get_callback_model_class(self) -> Union[BaseInput, None]:
        """Get callback model from 'callback_model' reference.

        Returns:
            BaseInput: Callback model of the input type
        """
        return self._get_class_from_reference(self.callback_model)

    def get_related_input_types(self) -> List[Self]:
        """Get relations between the different input types.

        Returns:
            Dict[InputType, List[InputType]]: Dict with a list of related input types for each input type
        """
        relations: List[InputType] = []
        model = self.get_model_class()
        if model:
            for field in model._meta.get_fields():  # For each model field
                # Check if field is a ForeignKey to a BaseInput model
                if field.__class__ == models.ForeignKey and issubclass(
                    field.related_model, BaseInput
                ):
                    # Search InputType by model
                    related_type = InputType.objects.filter(
                        model=f"{field.related_model._meta.app_label}.{field.related_model._meta.model_name}"
                    )
                    if related_type.exists():
                        relations.append(related_type.first())
        return relations