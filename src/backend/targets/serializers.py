from typing import Any

from framework.serializers import RelatedNotesSerializer
from platforms.defectdojo.serializers import DefectDojoTargetSyncSerializer
from rest_framework.serializers import ModelSerializer
from targets.models import Target


class SimpleTargetSerializer(ModelSerializer):
    """Simple serializer to include target main data in other serializers."""

    class Meta:
        model = Target
        fields = ("id", "project", "target", "type")


class TargetSerializer(RelatedNotesSerializer):
    """Serializer to manage targets via API."""

    defectdojo_sync = DefectDojoTargetSyncSerializer(many=False, read_only=True)

    class Meta:
        model = Target
        fields = (
            "id",
            "project",
            "target",
            "type",
            "target_ports",
            "tasks",
            "defectdojo_sync",
            "notes",
            "reports",
        )
        read_only_fields = (
            "type",
            "target_ports",
            "tasks",
            "defectdojo_sync",
            "reports",
            "notes",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate the provided data before use it.

        Args:
            attrs (dict[str, Any]): Provided data

        Returns:
            dict[str, Any]: Data after validation process
        """
        attrs = super().validate(attrs)
        attrs["type"] = Target.get_type(attrs["target"])
        return attrs
