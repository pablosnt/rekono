from typing import Any

from django.utils import timezone
from executions.serializers import SimpleExecutionSerializer
from findings.models import OSINT, Host
from rest_framework.serializers import ModelSerializer
from users.serializers import SimpleUserSerializer


class FindingSerializer(ModelSerializer):
    executions = SimpleExecutionSerializer(many=True, read_only=True)
    fixed_by = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        model = Host  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = (
            "id",
            "executions",
            "is_fixed",
            "auto_fixed",
            "fixed_date",
            "fixed_by",
            "defectdojo_id",
            "hacktricks_link",
            "notes",
        )
        read_only_fields = (
            "id",
            "executions",
            "auto_fixed",
            "fixed_date",
            "fixed_by",
            "defectdojo_id",
            "hacktricks_link",
            "notes",
        )


class TriageFindingSerializer(FindingSerializer):
    triage_by = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = FindingSerializer.Meta.fields + (
            "triage_status",
            "triage_comment",
            "triage_date",
            "triage_by",
        )
        read_only_fields = FindingSerializer.Meta.read_only_fields + (
            "triage_date",
            "triage_by",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        attrs["triage_date"] = timezone.now()
        attrs["triage_by"] = self.context.get("request").user
        return attrs
