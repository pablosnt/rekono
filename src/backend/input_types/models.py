"""Input types models for defining and managing different types of input data.

This module provides the InputType model which defines the different types of
input data that can be used as arguments in security tool executions. It manages
the relationships between input types and their corresponding Django models, enabling
dynamic discovery and validation of input data for comprehensive security testing.
"""

from functools import cached_property
from typing import Self

from django.apps import apps
from django.db import models

from framework.models import BaseInput, BaseModel
from input_types.enums import InputTypeName


class InputType(BaseModel):
    """Input type model for defining different categories of input data used in tool arguments.

    This model represents the different categories of input data that can be provided
    to security tools during execution. Each input type is associated with a specific
    Django model that handles the actual data storage and processing, enabling dynamic
    tool integration and flexible data handling.

    The model supports both primary and fallback model references, allowing for
    graceful degradation when the primary model is not available. It also tracks
    whether relationships should be calculated for this input type, enabling
    performance optimization for complex tool workflows.

    Attributes:
        name (TextField): The name of the input type from InputTypeName enum (max 15 chars).
        model (TextField): Reference to the primary Django model in 'app.Model' format
                          (optional, max 30 chars). Can reference Finding models.
        fallback_model (TextField): Reference to a fallback Django model when primary
                                   is unavailable (optional, max 15 chars).
        relationships (BooleanField): Whether this input type should be included in
                                     relationship calculations between models and executions.

    Example:
        Create an input type for host data:

        ```python
        input_type = InputType.objects.create(
            name=InputTypeName.HOST,
            model="findings.Host",
            fallback_model="findings.OSINT",
            relationships=True
        )
        ```
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
            str: The name of the input type for display purposes.
        """
        return self.name

    def _get_class_from_reference(self, reference: str) -> BaseInput | None:
        """Get a Django model class from a string reference.

        This helper method converts a string reference in 'app.Model' format
        to the actual Django model class. It's used internally by other
        methods to resolve model references dynamically.

        Args:
            reference (str): String reference in 'app.Model' format.

        Returns:
            BaseInput | None: The Django model class if found, None otherwise.
        """
        if not reference:
            return None
        app_label, model_name = reference.split(".", 1)
        return apps.get_model(app_label=app_label, model_name=model_name)

    @cached_property
    def model_class(self) -> BaseInput | None:
        """Get the primary model class associated with this input type.

        Returns:
            BaseInput | None: The primary Django model class if defined and available,
                             None if not defined or model cannot be resolved.
            ```
        """
        return self._get_class_from_reference(self.model)

    @cached_property
    def fallback_model_class(self) -> BaseInput | None:
        """Get the fallback model class associated with this input type.

        Returns:
            BaseInput | None: The fallback Django model class if defined and available,
                             None if not defined or model cannot be resolved.
        """
        return self._get_class_from_reference(self.fallback_model)

    @cached_property
    def parent_input_types(self) -> list[Self]:
        return self._get_related_input_types(models.ForeignKey)

    @cached_property
    def children_input_types(self) -> list[Self]:
        return self._get_related_input_types(models.ManyToOneRel)

    def _get_related_input_types(self, related_field_class: type) -> list[Self]:
        relations: list[InputType] = []
        if not self.relationships:
            return relations
        if self.model_class:
            # Iterate through all fields in the model to find foreign key relationships
            for field in self.model_class._meta.get_fields():
                # Check if field is a ForeignKey to a BaseInput model
                if field.__class__ == related_field_class and issubclass(field.related_model, BaseInput):
                    # Search InputType by model reference
                    related_type = InputType.objects.filter(
                        model=f"{field.related_model._meta.app_label}.{field.related_model._meta.model_name}"
                    )
                    if related_type.exists():
                        relations.append(related_type.first())
        return relations
