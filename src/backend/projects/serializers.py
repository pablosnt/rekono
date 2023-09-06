import logging
from typing import Any, Dict

from django.db import transaction
from framework.fields import TagField
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
        )
        read_only_fields = (
            "owner",
            "targets",
            "members",
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
        return project


class ProjectMemberSerializer(Serializer):
    """Serializer to add new member to a project via API."""

    user = IntegerField(required=True)

    @transaction.atomic()
    def update(self, instance: Project, validated_data: Dict[str, Any]) -> Project:
        """Update instance from validated data.

        Args:
            instance (Project): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Project: Updated instance
        """
        user = User.objects.get(pk=validated_data.get("user"), is_active=True)
        instance.members.add(user)
        return instance
