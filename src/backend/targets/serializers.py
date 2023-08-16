from typing import Any, Dict

from rest_framework.serializers import ModelSerializer
from targets.models import Target


class SimpleTargetSerializer(ModelSerializer):
    """Simple serializer to include target main data in other serializers."""

    class Meta:
        model = Target
        fields = ("id", "project", "target", "type")  # Target fields exposed via API


class TargetSerializer(ModelSerializer):
    """Serializer to manage targets via API."""

    class Meta:
        model = Target
        fields = (  # Target fields exposed via API
            "id",
            "project",
            "target",
            "type",
            "target_ports",
            "input_technologies",
            "input_vulnerabilities",
            # "tasks",
        )
        read_only_fields = (  # Read only fields
            "type",
            "target_ports",
            "input_technologies",
            "input_vulnerabilities",
            # "tasks",
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
