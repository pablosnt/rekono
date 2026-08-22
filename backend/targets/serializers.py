"""Serializers of the target endpoints."""

from typing import Any

from rest_framework.serializers import ModelSerializer

from framework.serializers import RelatedNotesSerializer
from platforms.defectdojo.serializers import DefectDojoTargetSyncSerializer
from targets.models import Target


class SimpleTargetSerializer(ModelSerializer):
    """Serializer with the minimum data needed to reference a target."""

    class Meta:
        """Serializer configuration for the target references."""

        model = Target
        fields = ("id", "project", "target", "type")


class TargetSerializer(RelatedNotesSerializer):
    """Serializer of a target, including the entities related to it.

    Attributes:
        defectdojo_sync: Synchronization of the target with a DefectDojo engagement,
          if it's configured.
    """

    defectdojo_sync = DefectDojoTargetSyncSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration for the targets."""

        model = Target
        fields = ("id", "project", "target", "type", "target_ports", "tasks", "defectdojo_sync", "notes", "reports")
        read_only_fields = ("type", "target_ports", "tasks", "defectdojo_sync", "reports", "notes")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Detect the type of the target, which the users don't provide.

        Args:
            attrs: Target fields sent by the user.

        Returns:
            The validated data with the detected type added, since the type is a
            read-only field that the request never carries.
        """
        attrs = super().validate(attrs)
        attrs["type"] = Target.get_type(attrs["target"])
        return attrs
