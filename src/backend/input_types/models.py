from typing import Optional, Self

from django.apps import apps
from django.db import models
from framework.models import BaseInput, BaseModel
from input_types.enums import InputTypeName

# Create your models here.


class InputType(BaseModel):
    """Input type model, related to each object type that can be included in a tool argument."""

    name = models.TextField(max_length=15, choices=InputTypeName.choices)
    # Related model name in 'app.Model' format. It can be a reference to a Finding
    model = models.TextField(max_length=30, blank=True, null=True)
    # Related callback model name in 'app.Model' format. It will be used when 'model' is not available
    fallback_model = models.TextField(max_length=15, blank=True, null=True)
    # Indicate if the input type should be included to calculate relations between models and executions
    relationships = models.BooleanField(default=True)

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.name

    def _get_class_from_reference(self, reference: str) -> BaseInput:
        if not reference:
            return None
        app_label, model_name = reference.split(".", 1)
        return apps.get_model(app_label=app_label, model_name=model_name)

    def get_model_class(self) -> Optional[BaseInput]:
        """Get related model from 'model' reference.

        Returns:
            BaseInput: Related model of the input type
        """
        return self._get_class_from_reference(self.model)

    def get_fallback_model_class(self) -> Optional[BaseInput]:
        """Get callback model from 'fallback_model' reference.

        Returns:
            BaseInput: Callback model of the input type
        """
        return self._get_class_from_reference(self.fallback_model)

    def get_related_input_types(self) -> list[Self]:
        """Get relations between the different input types.

        Returns:
            dict[InputType, list[InputType]]: dict with a list of related input types for each input type
        """
        relations: list[InputType] = []
        if not self.relationships:
            return relations
        model = self.get_model_class()
        if model:
            for field in model._meta.get_fields():  # For each model field
                # Check if field is a ForeignKey to a BaseInput model
                if field.__class__ == models.ForeignKey and issubclass(field.related_model, BaseInput):
                    # Search InputType by model
                    related_type = InputType.objects.filter(
                        model=f"{field.related_model._meta.app_label}.{field.related_model._meta.model_name}"
                    )
                    if related_type.exists():
                        relations.append(related_type.first())
        return relations
