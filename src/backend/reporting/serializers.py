from typing import Any, Dict

from django.core.exceptions import ValidationError
from findings.enums import TriageStatus
from projects.models import Project
from reporting.enums import FindingName, ReportFormat
from reporting.models import Report
from rest_framework.serializers import (
    BooleanField,
    ModelSerializer,
    MultipleChoiceField,
)
from targets.models import Target
from tasks.models import Task


class ReportSerializer(ModelSerializer):
    class Meta:
        model = Report
        fields = ("id", "project", "target", "task", "status", "format", "user", "date")


class CreateReportSerializer(ModelSerializer):
    only_true_positives = BooleanField(required=False, write_only=True)
    finding_types = MultipleChoiceField(
        choices=FindingName.choices, required=False, write_only=True
    )
    validated_filter = {}
    validated_finding_types = []

    # TODO: Allow PDF encryption with the Rekono password:
    # - Ask users for password
    # - Validate Rekono password
    # - Encrypt file with Rekono password
    # - Store in database if reports are encrypted or not, and skip them from the querysets of the other users

    class Meta:
        model = Report
        fields = (
            "id",
            "project",
            "target",
            "task",
            "format",
            "only_true_positives",
            "finding_types",
            "user",
        )
        read_only_fields = ("user",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        self.validated_filter = {}
        no_mandatory_field = True
        for field, filter_field in [
            ("task", "executions__task"),
            ("target", "executions__task__target"),
            ("project", "executions__task__target__project"),
        ]:
            value = attrs.get(field)
            if value:
                no_mandatory_field = False
                self.validated_filter = {filter_field: value} if attrs.get("format") != ReportFormat.PDF else {}
                only_true_positives = attrs.pop("only_true_positives", False)
                if only_true_positives:
                    self.validated_filter.update(
                        {"triage_status": TriageStatus.TRUE_POSITIVE}
                    )
                else:
                    self.validated_filter.update(
                        {
                            "triage_status__in": [
                                TriageStatus.UNTRIAGED,
                                TriageStatus.WONT_FIX,
                                TriageStatus.TRUE_POSITIVE,
                            ]
                        }
                    )
                break
        if no_mandatory_field:
            raise ValidationError(
                "At lest one task, target or project must be provided", code="report"
            )
        self.validated_finding_types = (
            attrs.pop("finding_types")
            if attrs.get("format") != ReportFormat.PDF
            else None
        ) or list(FindingName)
        return attrs
