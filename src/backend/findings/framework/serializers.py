from typing import Any, Dict

from django.utils import timezone
from findings.models import OSINT
from rest_framework.serializers import ModelSerializer


class FindingSerializer(ModelSerializer):
    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = (
            "id",
            "executions",
            "is_fixed",
            "fixed_date",
            "fixed_by",
            "defect_dojo_id",
            "hacktricks_link",
        )


class TriageFindingSerializer(ModelSerializer):
    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = FindingSerializer.Meta.fields + (
            "triage_status",
            "triage_comment",
            "triage_date",
            "triage_by",
        )
        read_only_fields = FindingSerializer.Meta.fields + ("triage_date", "triage_by")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        attrs["triage_date"] = timezone.now()
        attrs["triage_by"] = self.context.get("request").user
        return attrs
