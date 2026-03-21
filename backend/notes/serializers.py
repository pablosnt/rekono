"""Django REST framework serializers for notes management.

Serializer classes for converting note models to/from JSON for API operations.
Includes validation logic for entity relationships, forking behavior, and
collaborative features with tag support.
"""

from typing import Any, cast

from rest_framework.fields import ValidationError
from rest_framework.serializers import SerializerMethodField
from taggit.serializers import TaggitSerializer

from framework.fields import TagField
from framework.models import BaseModel
from framework.serializers import LikeSerializer
from notes.models import Note
from users.serializers import SimpleUserSerializer

# List of all possible entity relationships for notes
# Used for validation and project context determination
links = [
    "project",
    "target",
    "task",
    "osint",
    "host",
    "port",
    "path",
    "credential",
    "technology",
    "vulnerability",
    "exploit",
]


class NoteSerializer(TaggitSerializer, LikeSerializer):
    """Serializer for Note model with collaborative features.

    Handles serialization and deserialization of Note objects for API operations.
    Includes validation logic for entity relationships, forking behavior, and
    tag management with computed fields for fork status.

    Attributes:
        owner (SimpleUserSerializer): Serialized user information for note owner
        tags (TagField): Tag field for note categorization
        forked (SerializerMethodField): Whether current user has forked this note
    """

    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()
    forked = SerializerMethodField(read_only=True)

    class Meta:
        """Meta configuration for the NoteSerializer.

        Attributes:
            model (Model): The Note model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified via API
        """

        model = Note
        fields = (
            ("id",)
            + tuple(links)
            + (
                "title",
                "body",
                "tags",
                "owner",
                "public",
                "forked",
                "forked_from",
                "forks",
                "created_at",
                "updated_at",
                "liked",
                "likes",
            )
        )
        read_only_fields = (
            "owner",
            "forked",
            "forked_from",
            "forks",
            "created_at",
            "updated_at",
            "liked",
            "likes",
        )

    def get_forked(self, instance: Any) -> bool:
        """Check if the current user has forked this note.

        Args:
            instance (Note): The note instance being serialized

        Returns:
            bool: True if the current user has forked this note, False otherwise
        """
        return instance.forks.filter(owner=self.context.get("request").user).exists()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate note data and ensure single entity association.

        Ensures that a note is associated with exactly one entity and automatically
        sets the project context based on the associated entity.

        Args:
            attrs (dict[str, Any]): Validated field data

        Returns:
            dict[str, Any]: Validated and processed field data

        Raises:
            ValidationError: If no project context can be determined
        """
        attrs = super().validate(attrs)
        # Find the first (most specific) entity relationship in the data
        # Reverse order ensures we get the most specific entity first
        data_links = [link for link in reversed(links) if attrs.get(link) is not None]
        if len(data_links) > 0:
            # Clear all other entity relationships to ensure only one is active
            for link in links:
                if link != data_links[0]:
                    attrs[link] = None
            # Set project context from the active entity
            attrs["project"] = cast(BaseModel, attrs.get(data_links[0])).parent_project
        return attrs

    def update(self, instance: Note, validated_data: dict[str, Any]) -> Note:
        """Update note instance with validation for project changes and fork behavior.

        Enforces project immutability and handles fork unlinking when notes become private.
        Ensures forked notes maintain proper visibility behavior.

        Args:
            instance (Note): The note instance being updated
            validated_data (dict[str, Any]): The validated update data

        Returns:
            Note: The updated note instance

        Raises:
            ValidationError: If attempting to change the project of an existing note
        """
        if instance.project != validated_data.get("project"):
            raise ValidationError("You are not allowed to change the project of a note", code="project")
        # Forked notes cannot be made public - they must remain private
        if instance.forked_from and validated_data.get("public", True):
            validated_data["public"] = False
        # Track if we need to unlink forks when a note becomes private
        unlink_forks = instance.public and not validated_data.get("public", False)
        # Perform the update
        new_instance = super().update(instance, validated_data)
        # If the note became private, unlink all its forks
        if unlink_forks:
            Note.objects.filter(public=False, forked_from=new_instance).update(forked_from=None)
        return new_instance
