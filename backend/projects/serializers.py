"""Django REST framework serializers for project management.

Provides serializer classes for project model conversion to/from JSON with
automated project setup including owner membership and default alert creation.
"""

from typing import Any

from django.db import transaction
from taggit.serializers import TaggitSerializer

from alerts.enums import AlertItem
from alerts.models import Alert
from framework.fields import TagField
from framework.serializers import RelatedNotesSerializer
from platforms.defectdojo.serializers import DefectDojoSyncSerializer
from projects.models import Project
from targets.serializers import SimpleTargetSerializer
from users.serializers import SimpleUserSerializer


class ProjectSerializer(TaggitSerializer, RelatedNotesSerializer):
    """Serializer for Project model with automated setup and nested relationships.

    Handles serialization and deserialization of Project objects with support
    for tagging, nested relationships, and automated project initialization
    including owner membership and default security monitoring alerts.

    Attributes:
        targets (SimpleTargetSerializer): Nested target information for project
        owner (SimpleUserSerializer): Serialized user information for project owner
        tags (TagField): Project organizational tags with tagging support
        defectdojo_sync (DefectDojoSyncSerializer): DefectDojo integration configuration
    """

    targets = SimpleTargetSerializer(read_only=True, many=True)
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()  # Tags
    defectdojo_sync = DefectDojoSyncSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for the ProjectSerializer.

        Attributes:
            model (Model): The Project model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified
        """

        model = Project
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "targets",
            "members",
            "tags",
            "defectdojo_sync",
            "notes",  # TODO: Is it really needed?
        )
        read_only_fields = (
            "owner",
            "targets",
            "members",
            "defectdojo_sync",
            "notes",
        )

    @transaction.atomic()
    def create(self, validated_data: dict[str, Any]) -> Project:
        """Create a new project with automated setup and default configuration.

        Creates a new project and performs automated initialization including
        adding the owner to the member list and creating a default trending
        CVE monitoring alert with owner subscription.

        Args:
            validated_data (dict[str, Any]): The validated data for creating the project

        Returns:
            Project: The created Project instance with automated configuration
        """
        project = super().create(validated_data)
        # Add project owner also in member list
        project.members.add(validated_data.get("owner"))
        # Create trending CVE monitor alert by default
        alert = Alert.objects.create(
            project=project,
            item=AlertItem.TRENDING_CVE,
            value=str(True).lower(),
            enabled=True,
            owner=validated_data.get("owner"),
            subscribe_all_members=True,
        )
        alert.subscribers.add(validated_data.get("owner"))
        return project
