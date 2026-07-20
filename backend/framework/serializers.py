"""Django REST framework serializers for Rekono's core framework.

Provides base serializer classes with like functionality and note relationships
for user-interactive content across the platform.
"""

from typing import Any

from django.db.models import Q
from rest_framework.serializers import BooleanField, IntegerField, ModelSerializer, SerializerMethodField

from framework.logging import LoggingEntity


class LikeSerializer(ModelSerializer, LoggingEntity):
    """Base serializer for models with like/favorite functionality.

    Exposes like status and counts for user-interactive content such as tools,
    processes, and wordlists. Both fields are read-only and their values come
    directly from the queryset annotations applied in LikeViewSet.get_queryset(),
    so the calculation lives in a single place and stays usable for ordering.

    Attributes:
        liked (BooleanField): Whether the current user has liked the object.
        likes (IntegerField): Total number of likes for the object.
    """

    liked = BooleanField(read_only=True)
    likes = IntegerField(read_only=True)


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
