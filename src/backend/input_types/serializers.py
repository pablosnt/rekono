"""Serializers for the input_types app.

This module provides Django REST Framework serializers for the InputType model,
enabling API serialization and deserialization of input type data.
"""

from rest_framework.serializers import ModelSerializer

from input_types.models import InputType


class InputTypeSerializer(ModelSerializer):
    """Serializer for the InputType model.

    This serializer handles the conversion of InputType model instances to and
    from JSON format for API communication. It exposes the essential fields
    needed for input type management.

    The serializer includes the name, model reference, and fallback model
    reference fields, which are the core attributes needed for input type
    configuration and relationship management.
    """

    class Meta:
        """Meta configuration for the InputTypeSerializer.

        This inner class defines the serializer's configuration, specifying
        which model to serialize and which fields to include in the serialized
        output. It controls the API representation of InputType instances.

        Attributes:
            model: The Django model class to serialize (InputType).
            fields: Tuple of field names to include in serialization.
        """

        model = InputType
        fields = (
            "name",
            "model",
            "fallback_model",
        )
