"""Serializers for the notes app.

This module provides Django REST Framework serializers for the Note model,
enabling API serialization and deserialization of note data with complex
validation logic for entity relationships and forking functionality.
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
    "execution",
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
    """Serializer for the Note model with complex validation and forking support.

    This serializer handles the conversion of Note model instances to and from
    JSON format for API communication. It includes complex validation logic for
    entity relationships, forking functionality, and project context determination.

    The serializer ensures that only one entity relationship is active at a time
    and automatically determines the project context from the related entity.
    It also handles forking logic, ensuring forked notes remain public and
    managing fork relationships when notes become private.

    Attributes:
        owner: Serialized user information (read-only).
        tags: Tag field with custom tag handling.
        forked: Computed field indicating if the current user has forked this note.
    """

    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()
    forked = SerializerMethodField(read_only=True)

    class Meta:
        """Meta configuration for the NoteSerializer.

        This inner class defines the serializer's configuration, specifying
        which model to serialize, which fields to include, and which fields
        should be read-only.

        Attributes:
            model: The Django model class to serialize (Note).
            fields: Tuple of field names to include in serialization.
            read_only_fields: Tuple of field names that cannot be modified
                through the API.
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
            instance: The Note instance to check.

        Returns:
            True if the current user has forked this note, False otherwise.
        """
        return instance.forks.filter(owner=self.context.get("request").user).exists()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate note data and ensure proper entity relationships.

        This method performs complex validation to ensure:
        1. Only one entity relationship is active at a time
        2. The project context is properly determined from the related entity
        3. A valid project relationship exists

        Args:
            attrs: The attributes to validate.

        Returns:
            The validated attributes with proper entity relationships.

        Raises:
            ValidationError: If no valid project relationship is found.
        """
        attrs = super().validate(attrs)
        # Find the first (most specific) entity relationship in the data
        # Reverse order ensures we get the most specific entity first
        data_links = [link for link in reversed(links) if attrs.get(link)]

        if len(data_links) > 0:
            # Clear all other entity relationships to ensure only one is active
            for link in links:
                if link != data_links[0]:
                    attrs[link] = None
            # Set project context from the active entity
            attrs["project"] = cast(BaseModel, attrs.get(data_links[0])).parent_project
        # Ensure a project relationship exists
        if not attrs.get("project"):
            raise ValidationError("A relationship with a project entity is needed", code="project")
        return attrs

    def update(self, instance: Note, validated_data: dict[str, Any]) -> Note:
        """Update a note instance with special handling for forking logic.

        This method handles the complex logic for updating notes, particularly
        around forking relationships and privacy settings:

        1. Forked notes cannot be made private (they must remain public)
        2. When a public note becomes private, all its forks are unlinked

        Args:
            instance: The Note instance to update.
            validated_data: The validated data for the update.

        Returns:
            The updated Note instance.
        """
        if instance.project != validated_data.get("project"):
            raise ValidationError("You are not allowed to change the project of a note", code="project")
        # Forked notes cannot be made private - they must remain public
        if instance.forked_from and validated_data.get("public", False):
            validated_data["public"] = True
        # Track if we need to unlink forks when a note becomes private
        unlink_forks = instance.public and not validated_data.get("public", False)
        # Perform the update
        new_instance = super().update(instance, validated_data)
        # If the note became private, unlink all its forks
        if unlink_forks:
            Note.objects.filter(public=False, forked_from=new_instance).update(forked_from=None)
        return new_instance
