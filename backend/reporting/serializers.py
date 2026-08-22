"""Serializers of the report endpoints."""

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
    """Serializer of a report and of the scope that it covers.

    Attributes:
        project: Project whose findings the report includes.
        target: Target whose findings the report includes.
        task: Task whose findings the report includes.
        user: User that requested the report.
    """

    project = ProjectSerializer(read_only=True, many=False)
    target = SimpleTargetSerializer(read_only=True, many=False)
    task = TaskSerializer(read_only=True, many=False)
    user = SimpleUserSerializer(read_only=True, many=False)

    class Meta:
        """Serializer configuration for the reports."""

        model = Report
        fields = ("id", "project", "target", "task", "status", "format", "user", "date")


class CreateReportSerializer(ModelSerializer):
    """Serializer of a new report and of the findings that it must include.

    The options that select the findings aren't stored, since the report is
    generated only once, so they are turned into the filters that the viewset
    applies when it queries the findings.

    Attributes:
        only_true_positives: Whether to include only the findings that the auditors
          confirmed, instead of everything that they haven't discarded.
        include_findings_from_user_input: Whether to include the findings created
          from the data that the users provided.
        finding_types: Finding types to include, which are all of them by default.
        validated_filter: Filters that select the findings of the report.
        validated_finding_types: Finding types that the report will include.
    """

    only_true_positives = BooleanField(required=False, write_only=True)
    include_findings_from_user_input = BooleanField(required=False, default=False, write_only=True)
    finding_types = MultipleChoiceField(choices=FindingName.choices, required=False, write_only=True)
    validated_filter: dict[str, Any] = {}
    validated_finding_types: list[FindingName] = []

    class Meta:
        """Serializer configuration for the report creation."""

        model = Report
        fields = (
            "id",
            "project",
            "target",
            "task",
            "format",
            "only_true_positives",
            "include_findings_from_user_input",
            "finding_types",
            "user",
        )
        read_only_fields = ("user",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the report data and build the filters that select its findings.

        Args:
            attrs: Report fields sent by the user, including the options that
              select the findings to include.

        Returns:
            The validated data, without the options that select the findings, since
            they aren't fields of the report. The triage filter is left apart from
            the rest, because it can only be applied to the findings that the
            auditors review one by one.

        Raises:
            ValidationError: If the report has no scope, which is the project, the
              target, or the task whose findings it includes.
        """
        attrs = super().validate(attrs)
        self.validated_filter = {"is_fixed": False}
        if not attrs.pop("include_findings_from_user_input", False):
            self.validated_filter["created_from_user_input"] = False
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
        # The most specific scope wins, so a report of one task doesn't include the rest of
        # the findings of its target
        for field, filter_field in [
            ("task", "executions__task"),
            ("target", "executions__task__target"),
            ("project", "executions__task__target__project"),
        ]:
            value = attrs.get(field)
            if value:
                no_mandatory_field = False
                # The PDF report is structured by target, so it queries the findings of each
                # target apart instead of using one filter for the whole scope
                if attrs.get("format") != ReportFormat.PDF:
                    self.validated_filter[filter_field] = value
                break
        if no_mandatory_field:
            raise ValidationError("At lest one task, target or project must be provided", code="report")
        # Finding types included in PDF reports are not customizable
        finding_types = attrs.pop("finding_types", None)
        if finding_types and attrs.get("format") != ReportFormat.PDF:
            self.validated_finding_types = finding_types
        else:
            self.validated_finding_types = list(FindingName)
        return attrs
