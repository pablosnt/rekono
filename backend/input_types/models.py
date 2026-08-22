"""Model of the input types that the tools can take as arguments.

The input types are seeded from a fixture, so they are looked up by name instead of
being created at runtime, and each one resolves the Django model that stores its
data from a string reference to avoid circular imports between the apps.
"""

from functools import cached_property
from typing import Self

from django.apps import apps
from django.db import models

from framework.models import BaseInput, BaseModel
from input_types.enums import InputTypeName


class InputType(BaseModel):
    """Kind of data that a tool argument takes, and the model that stores it.

    Attributes:
        name: Name of the input type, which is unique within the catalog.
        model: Related model in 'app.Model' format, usually a finding.
        fallback_model: Model used when no data of the main model is available,
          like the targets when no host has been discovered yet.
        relationships: Whether the executions that provide this input type must be
          related to the ones that need it, which doesn't apply to the input types
          that the users create, like the wordlists.
    """

    name = models.TextField(max_length=15, choices=InputTypeName.choices)
    model = models.TextField(max_length=30, blank=True, null=True)
    fallback_model = models.TextField(max_length=15, blank=True, null=True)
    relationships = models.BooleanField(default=True)

    def __str__(self) -> str:
        """Return the name of the input type."""
        return self.name

    def _get_class_from_reference(self, reference: str) -> BaseInput | None:
        """Get the model class referenced by an app and model name.

        Args:
            reference: Reference in "app_label.model_name" form, or empty for the
              input types that don't declare that model.

        Returns:
            The model class, or None when there is no reference.
        """
        if not reference:
            return None
        app_label, model_name = reference.split(".", 1)
        return apps.get_model(app_label=app_label, model_name=model_name)

    @cached_property
    def model_class(self) -> BaseInput | None:
        """The model that stores this input type, or None if it has no model."""
        return self._get_class_from_reference(self.model)

    @cached_property
    def fallback_model_class(self) -> BaseInput | None:
        """The fallback model of this input type, or None if it has no fallback."""
        return self._get_class_from_reference(self.fallback_model)

    @cached_property
    def parent_input_types(self) -> list[Self]:
        """The input types whose data this one is discovered from."""
        return self._get_related_input_types(models.ForeignKey)

    @cached_property
    def children_input_types(self) -> list[Self]:
        """The input types that are discovered from this one's data."""
        return self._get_related_input_types(models.ManyToOneRel)

    def _get_related_input_types(self, related_field_class: type) -> list[Self]:
        """Get the input types related to this one by a kind of model field.

        Args:
            related_field_class: Field class that links the models, which is a
              ForeignKey to get the parents and a ManyToOneRel to get the children.

        Returns:
            The input types whose model is related to this one's, or an empty list
            if this input type doesn't take part in the relations between models.
        """
        relations: list[InputType] = []
        if not self.relationships:
            return relations
        if self.model_class is not None and hasattr(self.model_class, "_meta"):
            for field in self.model_class._meta.get_fields():
                # Only the relations between input models are relevant, since the other ones,
                # like the relation with the executions, are shared by all the findings
                if field.__class__ == related_field_class and issubclass(field.related_model, BaseInput):
                    related_type = InputType.objects.filter(
                        model=f"{field.related_model._meta.app_label}.{field.related_model._meta.model_name}"
                    )
                    if related_type.exists():
                        relations.append(related_type.first())
        return relations
