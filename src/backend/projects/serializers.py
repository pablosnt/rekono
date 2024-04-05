import logging
from typing import Any, Dict

from alerts.enums import AlertItem, AlertMode
from alerts.models import Alert
from django.db import transaction
from django.shortcuts import get_object_or_404
from framework.fields import TagField
from platforms.defect_dojo.serializers import DefectDojoSyncSerializer
from projects.models import Project
from rest_framework.serializers import IntegerField, ModelSerializer, Serializer
from taggit.serializers import TaggitSerializer
from targets.serializers import SimpleTargetSerializer
from users.models import User
from users.serializers import SimpleUserSerializer

logger = logging.getLogger()


class ProjectSerializer(TaggitSerializer, ModelSerializer):
    """Serializer to manage projects via API."""

    # Target details for read operations
    targets = SimpleTargetSerializer(read_only=True, many=True)
    # Owner details for read operations
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()  # Tags
    defect_dojo_sync = DefectDojoSyncSerializer(many=False, read_only=True)

    class Meta:
        """Serializer metadata."""

        model = Project
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "targets",
            "members",
            "tags",
            "defect_dojo_sync",
            "notes",
        )
        read_only_fields = (
            "owner",
            "targets",
            "members",
            "defect_dojo_sync",
            "notes",
        )

    @transaction.atomic()
    def create(self, validated_data: Dict[str, Any]) -> Project:
        """Create instance from validated data.

        Args:
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Project: Created instance
        """
        project = super().create(validated_data)  # Create project
        # Add project owner also in member list
        project.members.add(validated_data.get("owner"))
        alert = Alert.objects.create(
            project=project,
            item=AlertItem.CVE,
            mode=AlertMode.MONITOR,
            enabled=True,
            owner=validated_data.get("owner"),
        )
        alert.suscribers.add(validated_data.get("owner"))
        return project


class ProjectMemberSerializer(Serializer):
    """Serializer to add new member to a project via API."""

    user = IntegerField(required=True)

    def update(self, instance: Project, validated_data: Dict[str, Any]) -> Project:
        """Update instance from validated data.

        Args:
            instance (Project): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Project: Updated instance
        """
        user = get_object_or_404(User, pk=validated_data.get("user"), is_active=True)
        instance.members.add(user)
        for alert in Alert.objects.filter(
            project=instance, suscribe_all_members=True, enabled=True
        ).all():
            alert.suscribers.add(user)
        return instance
