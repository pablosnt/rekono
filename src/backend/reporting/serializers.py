"""Django REST framework serializers for security report models.

Provides serialization for report models with nested relationship data,
validation logic for report creation, and filtering configuration.
"""

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
    """Serializer for Report model with nested relationship data.

    Handles serialization of Report instances with detailed nested information
    for project, target, task, and user relationships in API responses.
    """

    project = ProjectSerializer(read_only=True, many=False)
    target = SimpleTargetSerializer(read_only=True, many=False)
    task = TaskSerializer(read_only=True, many=False)
    user = SimpleUserSerializer(read_only=True, many=False)

    class Meta:
        """Meta configuration for the ReportSerializer.

        Attributes:
            model (Model): The Report model to serialize.
            fields (tuple): Field names to include in serialization.
        """

        model = Report
        fields = ("id", "project", "target", "task", "status", "format", "user", "date")


class CreateReportSerializer(ModelSerializer):
    """Serializer for creating new security reports with filtering validation.

    Handles report creation with advanced filtering options including triage
    status filtering and finding type selection with validation logic.

    Attributes:
        only_true_positives (BooleanField): Filter to include only true positive findings (optional, write-only)
        include_findings_from_user_input (BooleanField): Include findings created from user input (optional, default=False, write-only)
        finding_types (MultipleChoiceField): Specific finding types to include in the report (optional, write-only)
        validated_filter (dict[str, Any]): Internal filter criteria applied during validation
        validated_finding_types (list[FindingName]): Internal list of validated finding types for report generation
    """

    only_true_positives = BooleanField(required=False, write_only=True)
    include_findings_from_user_input = BooleanField(required=False, default=False, write_only=True)
    finding_types = MultipleChoiceField(choices=FindingName.choices, required=False, write_only=True)
    validated_filter: dict[str, Any] = {}
    validated_finding_types: list[FindingName] = []

    class Meta:
        """Meta configuration for the CreateReportSerializer.

        Attributes:
            model (Model): The Report model to serialize.
            fields (tuple): Field names to include in serialization.
            read_only_fields (tuple): Fields that cannot be modified during creation.
        """

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
        """Validate report creation data and configure filtering criteria.

        Processes filtering options and validates that at least one scope
        (task, target, or project) is provided for the report.

        Args:
            attrs (dict[str, Any]): The attributes to validate

        Returns:
            dict[str, Any]: The validated attributes

        Raises:
            ValidationError: If no scope is provided for the report
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
        for field, filter_field in [
            ("task", "executions__task"),
            ("target", "executions__task__target"),
            ("project", "executions__task__target__project"),
        ]:
            value = attrs.get(field)
            if value:
                no_mandatory_field = False
                # PDF reports are splitting findings per target in order to structure the final document
                # That means that it doesn't make sense to create a filter valid to get all the findings together,
                # as if a project is specified, the generator will need to iterate over the project targets,
                # and then filter the findings by each target.
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
