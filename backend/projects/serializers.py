"""Serializers of the project endpoints."""

from typing import Any

from django.db import transaction
from taggit.serializers import TaggitSerializer

from alerts.enums import AlertItem
from alerts.models import Alert
from framework.fields import TagField
from framework.serializers import RelatedNotesSerializer
from platforms.defectdojo.serializers import DefectDojoSyncSerializer
from projects.models import Project
from users.serializers import SimpleUserSerializer


class ProjectSerializer(TaggitSerializer, RelatedNotesSerializer):
    """Serializer of a project, including the data of its related entities.

    Attributes:
        owner: User that created the project.
        tags: Labels assigned to the project.
        defectdojo_sync: Synchronization of the project with DefectDojo, if it's
          configured.
    """

    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()
    defectdojo_sync = DefectDojoSyncSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration for the projects."""

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
        """Create a project, with its owner as member and its default alert.

        The trending CVE alert is created enabled and with all the members
        subscribed, so a new project starts warning about the CVEs that are being
        exploited without anyone having to configure it.

        Args:
            validated_data: Project fields, plus the owner that the viewset adds
              when it saves the serializer, since the request never carries it.

        Returns:
            The created project, with its owner already added as a member.
        """
        project = super().create(validated_data)
        project.members.add(validated_data.get("owner"))
        alert = Alert.objects.create(
            project=project,
            item=AlertItem.TRENDING_CVE,
            value=str(True),
            enabled=True,
            owner=validated_data.get("owner"),
            subscribe_all_members=True,
        )
        alert.subscribers.add(validated_data.get("owner"))
        return project
