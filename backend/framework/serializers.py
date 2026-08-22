"""Base serializers shared by the Rekono apps.

Cover the two features that several models have in common: the likes given by the
users and the notes related to an object.
"""

from typing import Any

from django.db.models import Q
from rest_framework.serializers import BooleanField, IntegerField, ModelSerializer, SerializerMethodField

from framework.logging import LoggingEntity


class LikeSerializer(ModelSerializer, LoggingEntity):
    """Base serializer for the models that can be liked by the users.

    Both fields are read-only and their values come directly from the queryset
    annotations applied in LikeViewSet.get_queryset(), so the calculation lives in a
    single place and stays usable for ordering.

    Attributes:
        liked: Whether the user that performs the request liked this object.
        likes: Number of users that liked this object.
    """

    liked = BooleanField(read_only=True)
    likes = IntegerField(read_only=True)


class RelatedNotesSerializer(ModelSerializer, LoggingEntity):
    """Base serializer for the models that can be referenced from the notes.

    Attributes:
        notes: Identifiers of the related notes that the user can access.
    """

    notes = SerializerMethodField(read_only=True)

    def get_notes(self, instance: Any) -> list[int]:
        """Get the identifiers of the related notes visible to the current user.

        Args:
            instance: Object being serialized, whose related notes are filtered.

        Returns:
            The identifiers of the notes that are public or owned by the user that
            performs the request.
        """
        return instance.notes.filter(Q(public=True) | Q(owner__id=self.context.get("request").user.id)).values_list(
            "id", flat=True
        )
