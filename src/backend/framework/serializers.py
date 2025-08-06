
"""Django REST framework serializers for Rekono's core framework.

Provides base serializer classes with like functionality and note relationships
for user-interactive content across the platform.
"""

from typing import Any

from django.db.models import Q
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.logging import LoggingEntity
from users.models import User


class LikeSerializer(ModelSerializer, LoggingEntity):
    """Serializer for models with like/favorite functionality.

    Extends ModelSerializer with computed fields for like status and counts.
    Used for content that users can like such as tools, processes, and wordlists.

    Attributes:
        liked (SerializerMethodField): Whether current user has liked the object.
        likes (SerializerMethodField): Total number of likes for the object.
    """

    liked = SerializerMethodField(read_only=True)
    likes = SerializerMethodField(read_only=True)

    def get_liked(self, instance: Any) -> bool:
        """Check if the current user has liked this object.

        Args:
            instance (Any): The model instance being serialized.

        Returns:
            bool: True if the current user has liked this object, False otherwise.
        """
        check_likes = {
            "pk": self.context.get("request").user.id,
            f"liked_{instance.__class__.__name__.lower()}": instance,
        }
        return User.objects.filter(**check_likes).exists()

    def get_likes(self, instance: Any) -> int:
        """Get the total number of likes for this object.

        Args:
            instance (Any): The model instance being serialized.

        Returns:
            int: Total number of users who have liked this object.
        """
        return instance.liked_by.count()


class RelatedNotesSerializer(ModelSerializer, LoggingEntity):
    """Serializer for models with related notes functionality.

    Extends ModelSerializer with computed fields for accessing related notes
    that the current user can view based on visibility permissions.

    Attributes:
        notes (SerializerMethodField): List of note IDs accessible to current user.
    """

    notes = SerializerMethodField(read_only=True)

    def get_notes(self, instance: Any) -> list[int]:
        """Get list of note IDs that the current user can access.

        Returns notes that are either public or owned by the current user,
        ensuring proper access control for note visibility.

        Args:
            instance (Any): The model instance with related notes.

        Returns:
            list[int]: List of note IDs accessible to the current user.
        """
        return instance.notes.filter(Q(public=True) | Q(owner__id=self.context.get("request").user.id)).values_list(
            "id", flat=True
        )
