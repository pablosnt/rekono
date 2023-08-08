import logging
from typing import Any, Dict

from django.db import transaction
from framework.fields import TagField
from projects.models import Project
from rest_framework.serializers import ModelSerializer
from taggit.serializers import TaggitSerializer

logger = logging.getLogger()


class ProjectSerializer(TaggitSerializer, ModelSerializer):
    """Serializer to manage projects via API."""

    # Target details for read operations
    # targets = TargetSerializer(read_only=True, many=True)
    # Owner details for read operations
    # owner = SimplyUserSerializer(many=False, read_only=True)
    tags = TagField()  # Tags

    class Meta:
        """Serializer metadata."""

        model = Project
        fields = (
            "id",
            "name",
            "description",
            # "defectdojo_product_id",
            # "defectdojo_engagement_id",
            # "defectdojo_engagement_by_target",
            # "defectdojo_synchronization",
            # "owner",
            # "targets",
            # "members",
            "tags",
        )
        # read_only_fields = (
        #     "defectdojo_product_id",
        #     "defectdojo_engagement_id",
        #     "defectdojo_engagement_by_target",
        #     "defectdojo_synchronization",
        #     "owner",
        #     "targets",
        #     "members",
        # )

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
        # project.members.add(validated_data.get("owner"))
        return project


# class ProjectMemberSerializer(serializers.Serializer):
#     """Serializer to add new member to a project via API."""

#     user = serializers.IntegerField(
#         required=True
#     )  # User Id to add to the project members

#     @transaction.atomic()
#     def update(self, instance: Project, validated_data: Dict[str, Any]) -> Project:
#         """Update instance from validated data.

#         Args:
#             instance (Project): Instance to update
#             validated_data (Dict[str, Any]): Validated data

#         Returns:
#             Project: Updated instance
#         """
#         user = User.objects.get(
#             pk=validated_data.get("user"), is_active=True
#         )  # Get active user from user Id
#         instance.members.add(user)  # Add user as project member
#         return instance
