"""Django REST framework base serializers for input parameters.

Provides base serializer implementation for input parameter management
with automatic deduplication logic and validation capabilities.
"""

from typing import Any

from rest_framework.serializers import ModelSerializer

from parameters.models import InputTechnology, InputVulnerability


class InputParameterSerializer(ModelSerializer):
    """Base serializer for input parameters with deduplication logic.

    Provides common functionality for all input parameter serializers including
    automatic deduplication to prevent redundant parameter creation.

    Deduplication Logic:
        Before creating a new parameter, checks for existing parameters with
        identical field values and returns the existing instance if found.
    """

    def create(self, validated_data: dict[str, Any]) -> InputTechnology | InputVulnerability:
        """Create or retrieve existing input parameter with deduplication.

        Implements deduplication logic by searching for existing parameters
        with matching field values before creating a new instance.

        Args:
            validated_data (dict[str, Any]): Validated parameter data

        Returns:
            InputTechnology | InputVulnerability: Existing or newly created parameter instance
        """
        search = self.__class__.Meta.model.objects.filter(
            **{f: validated_data.get(f) for f in self.Meta.fields if f.lower() != "id"}
        )
        if search.exists():
            return search.first()
        return super().create(validated_data)
