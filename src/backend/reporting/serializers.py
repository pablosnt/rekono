from typing import Any, Dict

from django.core.exceptions import ValidationError
from findings.enums import TriageStatus
from reporting.enums import FindingName
from reporting.models import Report
from rest_framework.serializers import ModelSerializer, MultipleChoiceField


class ReportSerializer(ModelSerializer):
    class Meta:
        model = Report
        fields = ("id", "project", "target", "task", "status", "format", "user", "date")


class CreateReportSerializer(ModelSerializer):
    triage_statuses = MultipleChoiceField(
        choices=TriageStatus.choices, required=False, write_only=True
    )
    finding_types = MultipleChoiceField(
        choices=FindingName.choices, required=False, write_only=True
    )

    class Meta:
        model = Report
        fields = (
            "project",
            "target",
            "task",
            "format",
            "triage_statuses",
            "finding_types",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        self.filter = {}
        self.finding_types = attrs.pop("finding_types", [])
        no_mandatory_field = True
        for field, filter_field in [
            ("task", "executions__task"),
            ("target", "executions__task__target"),
            ("project", "executions__task__target__project"),
        ]:
            value = attrs.get(field)
            if value:
                no_mandatory_field = False
                self.filter = {filter_field: value}
                triage_statuses = attrs.pop("triage_statuses", [])
                if triage_statuses:
                    self.filter.update({"triage_status__in": triage_statuses})
                break
        if no_mandatory_field:
            raise ValidationError(
                "At lest one task, target or project must be provided", code="report"
            )
        return attrs
