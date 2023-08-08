from input_types.models import InputType
from rest_framework.serializers import ModelSerializer


class InputTypeSerializer(ModelSerializer):
    """Serializer to get the input type data via API."""

    class Meta:
        """Serializer metadata."""

        model = InputType
        fields = (
            "name",
            "model",
            "callback_model",
        )
