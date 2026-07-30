"""Django REST framework serializers for target models.

Provides serialization for target records with automatic type detection,
DefectDojo integration, and notes relationship support for comprehensive
API responses.
"""

from typing import Any

from rest_framework.serializers import ModelSerializer

from framework.serializers import RelatedNotesSerializer
from platforms.defectdojo.serializers import DefectDojoTargetSyncSerializer
from targets.models import Target


class SimpleTargetSerializer(ModelSerializer):
    """Simple serializer for Target model.

    Provides minimal view of target records with essential fields only
    for list views and basic information display.
    """

    class Meta:
        """Meta configuration for the SimpleTargetSerializer.

        Attributes:
            model (Model): The Target model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = Target
        fields = ("id", "project", "target", "type")


class TargetSerializer(RelatedNotesSerializer):
    """Serializer for Target model with comprehensive information.

    Provides detailed serialization including automatic type detection,
    DefectDojo synchronization data, related notes, and associated entities
    for complete API responses.

    Attributes:
        defectdojo_sync (DefectDojoTargetSyncSerializer): DefectDojo integration data
    """

    defectdojo_sync = DefectDojoTargetSyncSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for the TargetSerializer.

        Attributes:
            model (Model): The Target model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified
        """

        model = Target
        fields = ("id", "project", "target", "type", "target_ports", "tasks", "defectdojo_sync", "notes", "reports")
        read_only_fields = ("type", "target_ports", "tasks", "defectdojo_sync", "reports", "notes")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate target data with automatic type detection.

        Extends validation to automatically detect and set the target type
        based on the target specification using Target.get_type().

        Args:
            attrs (dict[str, Any]): The attributes to validate

        Returns:
            dict[str, Any]: The validated attributes with detected target type
        """
        attrs = super().validate(attrs)
        attrs["type"] = Target.get_type(attrs["target"])
        return attrs
