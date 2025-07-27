"""This module provides common serializers."""

from typing import Any

from django.db.models import Q
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.logging import LoggingEntity
from users.models import User


class LikeSerializer(ModelSerializer, LoggingEntity):
    """Serializer for likeable entities with like status and count.

    This serializer extends ModelSerializer to include computed fields
    that show whether the current user has liked the entity and the
    total number of likes.

    Attributes:
        liked (SerializerMethodField): Boolean indicating if current user liked.
        likes (SerializerMethodField): Total count of likes for the entity.
    """

    liked = SerializerMethodField(read_only=True)
    likes = SerializerMethodField(read_only=True)

    def get_liked(self, instance: Any) -> bool:
        """Check if the current user has liked this entity.

        Args:
            instance: The model instance being serialized.

        Returns:
            True if the current user has liked the entity, False otherwise.
        """
        check_likes = {
            "pk": self.context.get("request").user.id,
            f"liked_{instance.__class__.__name__.lower()}": instance,
        }
        return User.objects.filter(**check_likes).exists()

    def get_likes(self, instance: Any) -> int:
        """Get the total number of likes for this entity.

        Args:
            instance: The model instance being serialized.

        Returns:
            The total count of users who liked this entity.
        """
        return instance.liked_by.count()


class RelatedNotesSerializer(ModelSerializer, LoggingEntity):
    """Serializer for entities with related notes.

    This serializer includes a computed field that returns the IDs of
    notes that are either public or owned by the current user.

    Attributes:
        notes (SerializerMethodField): List of note IDs accessible to user.
    """

    notes = SerializerMethodField(read_only=True)

    def get_notes(self, instance: Any) -> list[int]:
        """Get accessible note IDs for this entity.

        Returns note IDs that are either public or owned by the current user.

        Args:
            instance: The model instance being serialized.

        Returns:
            List of note IDs that the current user can access.
        """
        return instance.notes.filter(Q(public=True) | Q(owner__id=self.context.get("request").user.id)).values_list(
            "id", flat=True
        )
