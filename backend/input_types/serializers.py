"""Serializer of the input type data.

The input types have no endpoints of their own, so this serializer is only used to
include them in the responses of the tool arguments.
"""

from rest_framework.serializers import ModelSerializer

from input_types.models import InputType


class InputTypeSerializer(ModelSerializer):
    """Serializer of the kind of data that a tool argument takes."""

    class Meta:
        """Serializer configuration for the input types."""

        model = InputType
        fields = (
            "name",
            "model",
            "fallback_model",
        )
