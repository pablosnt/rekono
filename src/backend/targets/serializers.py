from typing import Any, Dict

from rest_framework.serializers import ModelSerializer

from platforms.defect_dojo.serializers import DefectDojoTargetSyncSerializer
from targets.models import Target


class SimpleTargetSerializer(ModelSerializer):
    """Simple serializer to include target main data in other serializers."""

    class Meta:
        model = Target
        fields = ("id", "project", "target", "type")


class TargetSerializer(ModelSerializer):
    """Serializer to manage targets via API."""

    defect_dojo_sync = DefectDojoTargetSyncSerializer(many=False, read_only=True)

    class Meta:
        model = Target
        fields = (
            "id",
            "project",
            "target",
            "type",
            "target_ports",
            "input_technologies",
            "input_vulnerabilities",
            "tasks",
            "defect_dojo_sync",
            "notes",
        )
        read_only_fields = (
            "type",
            "target_ports",
            "input_technologies",
            "input_vulnerabilities",
            "tasks",
            "defect_dojo_sync",
            "notes",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Returns:
            Dict[str, Any]: Data after validation process
        """
        attrs = super().validate(attrs)
        attrs["type"] = Target.get_type(attrs["target"])
        return attrs
