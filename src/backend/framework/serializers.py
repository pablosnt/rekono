from typing import Any

from django.db.models import Q
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.logging import LoggingEntity
from users.models import User


class LikeSerializer(ModelSerializer, LoggingEntity):
    liked = SerializerMethodField(read_only=True)
    likes = SerializerMethodField(read_only=True)

    def get_liked(self, instance: Any) -> bool:
        check_likes = {
            "pk": self.context.get("request").user.id,
            f"liked_{instance.__class__.__name__.lower()}": instance,
        }
        return User.objects.filter(**check_likes).exists()

    def get_likes(self, instance: Any) -> int:
        return instance.liked_by.count()


class RelatedNotesSerializer(ModelSerializer, LoggingEntity):
    notes = SerializerMethodField(read_only=True)

    def get_notes(self, instance: Any) -> list[int]:
        return instance.notes.filter(Q(public=True) | Q(owner__id=self.context.get("request").user.id)).values_list(
            "id", flat=True
        )
