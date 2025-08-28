from typing import Any

from django.core.exceptions import ValidationError
from rest_framework.serializers import BooleanField, ModelSerializer, MultipleChoiceField

from findings.enums import TriageStatus
from projects.serializers import ProjectSerializer
from reporting.enums import FindingName, ReportFormat
from reporting.models import Report
from targets.serializers import SimpleTargetSerializer
from tasks.serializers import TaskSerializer
from users.serializers import SimpleUserSerializer


class ReportSerializer(ModelSerializer):
    project = ProjectSerializer(read_only=True, many=False)
    target = SimpleTargetSerializer(read_only=True, many=False)
    task = TaskSerializer(read_only=True, many=False)
    user = SimpleUserSerializer(read_only=True, many=False)

    class Meta:
        model = Report
        fields = ("id", "project", "target", "task", "status", "format", "user", "date")


class CreateReportSerializer(ModelSerializer):
    only_true_positives = BooleanField(required=False, write_only=True)
    finding_types = MultipleChoiceField(choices=FindingName.choices, required=False, write_only=True)
    validated_filter: dict[str, Any] = {}
    validated_finding_types: list[FindingName] = []

    class Meta:
        model = Report
        fields = ("id", "project", "target", "task", "format", "only_true_positives", "finding_types", "user")
        read_only_fields = ("user",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        self.validated_filter = {"is_fixed": False}
        self.validated_triage_filter = {}
        only_true_positives = attrs.pop("only_true_positives", False)
        if only_true_positives:
            self.validated_triage_filter.update({"triage_status": TriageStatus.TRUE_POSITIVE})
        else:
            self.validated_triage_filter.update(
                {
                    "triage_status__in": [
                        TriageStatus.UNTRIAGED,
                        TriageStatus.WONT_FIX,
                        TriageStatus.TRUE_POSITIVE,
                    ]
                }
            )
        no_mandatory_field = True
        for field, filter_field in [
            ("task", "executions__task"),
            ("target", "executions__task__target"),
            ("project", "executions__task__target__project"),
        ]:
            value = attrs.get(field)
            if value:
                no_mandatory_field = False
                # TODO: Why PDF is different?
                if attrs.get("format") != ReportFormat.PDF:
                    self.validated_filter[filter_field] = value
                break
        if no_mandatory_field:
            raise ValidationError("At lest one task, target or project must be provided", code="report")
        # Finding types included in PDF reports are not customizable
        if "finding_types" in attrs and attrs.get("finding_types") and attrs.get("format") != ReportFormat.PDF:
            self.validated_finding_types = attrs.pop("finding_types")
        else:
            self.validated_finding_types = list(FindingName)
        return attrs
