"""Base serializer classes for findings framework REST API.

Provides foundational serializer classes including FindingSerializer and
TriageFindingSerializer that all specific finding serializers inherit from
with standardized functionality for execution history and status tracking.
"""

from typing import Any

from django.utils import timezone
from rest_framework.serializers import SerializerMethodField

from executions.serializers import SimpleExecutionSerializer
from findings.framework.models import Finding
from findings.models import OSINT, Host
from framework.serializers import RelatedNotesSerializer
from users.serializers import SimpleUserSerializer


class FindingSerializer(RelatedNotesSerializer):
    """Base serializer for all finding types with execution tracking.

    Provides standardized JSON serialization for finding data including
    execution history, fixing status, and DefectDojo integration with
    proper field restrictions and nested relationships.

    Attributes:
        project (SerializerMethodField): Project ID the finding belongs to (read-only)
        executions (SimpleExecutionSerializer): Nested execution history (read-only)
        fixed_by (SimpleUserSerializer): User who fixed the finding (read-only)
    """

    project = SerializerMethodField(read_only=True)
    executions = SimpleExecutionSerializer(many=True, read_only=True)
    fixed_by = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for FindingSerializer.

        Defines model reference, included fields, and read-only restrictions
        for base finding serialization. Uses Host as default model reference.

        Attributes:
            model (type): Default model class (overridden by subclasses)
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields restricted from modification
        """

        model = Host  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = (
            "id",
            "project",
            "executions",
            "is_fixed",
            "auto_fixed",
            "fixed_date",
            "fixed_by",
            "created_from_user_input",
            "notes",
        )
        read_only_fields = (
            "id",
            "executions",
            "is_fixed",
            "auto_fixed",
            "fixed_date",
            "fixed_by",
            "created_from_user_input",
            "notes",
        )

    def get_project(self, instance: Finding) -> int:
        """Return the ID of the project the finding belongs to.

        Args:
            instance (Finding): The finding instance being serialized.

        Returns:
            int: The ID of the parent project.
        """
        return instance.parent_project.id


class HacktricksFindingSerializer(FindingSerializer):
    """Base serializer for findings enriched with HackTricks documentation.

    Extends FindingSerializer to expose the HackTricks documentation link for
    finding types supported by the HackTricks integration (hosts, ports, and
    technologies).
    """

    class Meta:
        """Meta configuration for HacktricksFindingSerializer.

        Extends FindingSerializer.Meta to include the read-only HackTricks
        documentation link.

        Attributes:
            model (type): Default model class (Host, overridden by subclasses)
            fields (tuple): Field names including the HackTricks link from parent
            read_only_fields (tuple): Fields restricted from modification including the HackTricks link
        """

        model = Host  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = FindingSerializer.Meta.fields + ("hacktricks_link",)
        read_only_fields = FindingSerializer.Meta.read_only_fields + ("hacktricks_link",)


class TriageFindingSerializer(FindingSerializer):
    """Base serializer for findings requiring triage workflow.

    Extends FindingSerializer to add triage functionality including
    status classification, comments, and audit tracking with automatic
    timestamp and user attribution.

    Attributes:
        triage_by (SimpleUserSerializer): User who performed triage (read-only)
    """

    triage_by = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for TriageFindingSerializer.

        Extends FindingSerializer.Meta to include triage-specific fields
        with automatic timestamp and user tracking.

        Attributes:
            model (type): Default model class (OSINT, overridden by subclasses)
            fields (tuple): Field names including triage fields from parent
            read_only_fields (tuple): Fields restricted from modification including triage metadata
        """

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
        """Validate triage data with automatic metadata assignment.

        Validates triage information and automatically assigns timestamp
        and user attribution for audit trail and tracking purposes.

        Args:
            attrs (dict[str, Any]): Attributes to validate and process.

        Returns:
            dict[str, Any]: Validated attributes with triage metadata added.
        """
        attrs = super().validate(attrs)
        attrs["triage_date"] = timezone.now()
        attrs["triage_by"] = self.context.get("request").user
        return attrs
