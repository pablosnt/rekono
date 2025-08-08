from typing import Any

from rest_framework.serializers import ModelSerializer

from framework.serializers import RelatedNotesSerializer
from platforms.defectdojo.serializers import DefectDojoTargetSyncSerializer
from targets.models import Target


class SimpleTargetSerializer(ModelSerializer):
    class Meta:
        model = Target
        fields = ("id", "project", "target", "type")


class TargetSerializer(RelatedNotesSerializer):
    defectdojo_sync = DefectDojoTargetSyncSerializer(many=False, read_only=True)

    class Meta:
        model = Target
        fields = ("id", "project", "target", "type", "target_ports", "tasks", "defectdojo_sync", "notes", "reports")
        read_only_fields = ("type", "target_ports", "tasks", "defectdojo_sync", "reports", "notes")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        attrs["type"] = Target.get_type(attrs["target"])
        return attrs
