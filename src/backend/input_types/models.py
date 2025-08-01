"""Input types module for defining and managing different types of input models.

This module provides the InputType model which defines the different types of
input data that can be used as arguments in tool executions. It manages the
relationships between input types and their corresponding Django models, enabling
dynamic discovery and validation of input data.
"""

from functools import cached_property
from typing import Self

from django.apps import apps
from django.db import models

from framework.models import BaseInput, BaseModel
from input_types.enums import InputTypeName


class InputType(BaseModel):
    """Input type model for defining different types of input models used in tool argument  s.

    This model represents the different categories of input models that can be provided
    to tools during execution. Each input type is associated with a specific Django
    model that handles the actual data storage and processing.

    The model supports both primary and fallback model references, allowing for
    flexible data handling when the primary model is not available. It also tracks
    whether relationships should be calculated for this input type.

    Attributes:
        name: The name of the input type (e.g., 'OSINT', 'HOST', 'PORT').
        model: Reference to the primary Django model in 'app.Model' format.
        fallback_model: Reference to a fallback Django model when primary is unavailable.
        relationships: Whether this input type should be included in relationship
            calculations.
    """

    name = models.TextField(max_length=15, choices=InputTypeName.choices)
    # Related model name in 'app.Model' format. It can be a reference to a Finding
    model = models.TextField(max_length=30, blank=True, null=True)
    # Related callback model name in 'app.Model' format. It will be used when 'model' is not available
    fallback_model = models.TextField(max_length=15, blank=True, null=True)
    # Indicate if the input type should be included to calculate relations between models and executions
    relationships = models.BooleanField(default=True)

    def __str__(self) -> str:
        """Return string representation of the input type.

        Returns:
            The name of the input type.
        """
        return self.name

    def _get_class_from_reference(self, reference: str) -> BaseInput | None:
        """Get a Django model class from a string reference.

        This helper method converts a string reference in 'app.Model' format
        to the actual Django model class. It's used internally by other
        methods to resolve model references.

        Args:
            reference: String reference in 'app.Model' format.

        Returns:
            The Django model class if found, None otherwise.
        """
        if not reference:
            return None
        app_label, model_name = reference.split(".", 1)
        return apps.get_model(app_label=app_label, model_name=model_name)

    @cached_property
    def model_class(self) -> BaseInput | None:
        """Get the primary model class associated with this input type.

        Returns:
            The primary Django model class if defined, None otherwise.
        """
        return self._get_class_from_reference(self.model)

    @cached_property
    def fallback_model_class(self) -> BaseInput | None:
        """Get the fallback model class associated with this input type.

        Returns:
            The fallback Django model class if defined, None otherwise.
        """
        return self._get_class_from_reference(self.fallback_model)

    @cached_property
    def related_input_types(self) -> list[Self]:
        """Get all input types that are related to this input type through foreign keys.

        This method analyzes the primary model's fields to find foreign key relationships
        to other BaseInput models. It then looks up the corresponding InputType instances
        for those related models.

        The method only processes relationships if the 'relationships' flag is True,
        allowing for performance optimization when relationship calculation is not needed.

        Returns:
            List of InputType instances that are related to this input type.
        """
        relations: list[InputType] = []
        if not self.relationships:
            return relations
        if self.model_class:
            # Iterate through all fields in the model to find foreign key relationships
            for field in self.model_class._meta.get_fields():
                # Check if field is a ForeignKey to a BaseInput model
                if field.__class__ == models.ForeignKey and issubclass(field.related_model, BaseInput):
                    # Search InputType by model reference
                    related_type = InputType.objects.filter(
                        model=f"{field.related_model._meta.app_label}.{field.related_model._meta.model_name}"
                    )
                    if related_type.exists():
                        relations.append(related_type.first())
        return relations
