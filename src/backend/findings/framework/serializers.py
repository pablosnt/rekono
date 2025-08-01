"""Base serializers for findings framework.

This module provides the foundational serializer classes for the findings system,
including FindingSerializer and TriageFindingSerializer that all specific
finding serializers inherit from. These provide standardized functionality
for serializing finding data including execution history, fixing status,
and triage information.
"""

from typing import Any

from django.utils import timezone

from executions.serializers import SimpleExecutionSerializer
from findings.models import OSINT, Host
from framework.serializers import RelatedNotesSerializer
from users.serializers import SimpleUserSerializer


class FindingSerializer(RelatedNotesSerializer):
    """Base serializer for all finding types.

    Provides standardized serialization for finding data including
    execution history, fixing status, and related notes. All specific
    finding serializers should inherit from this class.
    """

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
    """Base serializer for findings that require triage.

    Extends FindingSerializer to add triage functionality, including
    triage status, comments, and tracking information.
    """

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
        """Validate and prepare triage data.

        Automatically sets the triage date and user when triage
        information is being updated.

        Args:
            attrs: The attributes to validate.

        Returns:
            Validated attributes with triage metadata added.
        """
        attrs = super().validate(attrs)
        attrs["triage_date"] = timezone.now()
        attrs["triage_by"] = self.context.get("request").user
        return attrs
