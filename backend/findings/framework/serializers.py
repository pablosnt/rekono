"""Base serializers of the findings."""

from typing import Any

from django.utils import timezone
from rest_framework.serializers import SerializerMethodField

from executions.serializers import SimpleExecutionSerializer
from findings.framework.models import Finding
from findings.models import OSINT, Host
from framework.serializers import RelatedNotesSerializer
from users.serializers import SimpleUserSerializer


class FindingSerializer(RelatedNotesSerializer):
    """Base serializer of a finding, including where it was discovered.

    Attributes:
        project: Project that the finding belongs to.
        executions: Executions that discovered the finding.
        fixed_by: User that fixed the finding.
    """

    project = SerializerMethodField(read_only=True)
    executions = SimpleExecutionSerializer(many=True, read_only=True)
    fixed_by = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration shared by all the findings."""

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
        """Get the identifier of the project that the finding belongs to.

        Args:
            instance: Finding being serialized.

        Returns:
            The identifier of its project.
        """
        return instance.parent_project.id


class HacktricksFindingSerializer(FindingSerializer):
    """Base serializer of the findings that link to a HackTricks guide."""

    class Meta:
        """Serializer configuration adding the HackTricks link to the common one."""

        model = Host  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = FindingSerializer.Meta.fields + ("hacktricks_link",)
        read_only_fields = FindingSerializer.Meta.read_only_fields + ("hacktricks_link",)


class TriageFindingSerializer(FindingSerializer):
    """Base serializer of the findings that the auditors review one by one.

    Attributes:
        triage_by: User that reviewed the finding.
    """

    triage_by = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration adding the triage fields to the common ones."""

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
        """Record who reviewed the finding and when, which the users don't provide.

        Args:
            attrs: Triage values sent by the user.

        Returns:
            The values with triage_date and triage_by added. Both are read only
            fields, so they reach the update only because they are injected here.
        """
        attrs = super().validate(attrs)
        attrs["triage_date"] = timezone.now()
        attrs["triage_by"] = self.context.get("request").user
        return attrs
