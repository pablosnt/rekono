"""Django REST framework serializers for input type management.

Serializer classes for converting input type models to/from JSON
for API operations with essential field exposure.
"""

from rest_framework.serializers import ModelSerializer

from input_types.models import InputType


class InputTypeSerializer(ModelSerializer):
    """Serializer for InputType model.

    Handles serialization and deserialization of InputType objects for API operations.
    Exposes the core fields needed for input type configuration.
    """

    class Meta:
        """Meta configuration for the InputTypeSerializer.

        Attributes:
            model (Model): The InputType model to serialize.
            fields (tuple): Field names to include in serialization.
        """

        model = InputType
        fields = (
            "name",
            "model",
            "fallback_model",
        )
