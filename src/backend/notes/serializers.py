from typing import Any, Dict

from taggit.serializers import TaggitSerializer

from framework.fields import TagField
from framework.serializers import LikeSerializer
from notes.models import Note
from users.serializers import SimpleUserSerializer


class NoteSerializer(TaggitSerializer, LikeSerializer):
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()

    class Meta:
        model = Note
        fields = (
            "id",
            "project",
            "target",
            "title",
            "body",
            "tags",
            "owner",
            "public",
            "forked_from",
            "forks",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "forked_from", "forks", "created_at", "updated_at")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        if attrs.get("target"):
            attrs["project"] = None
        return attrs
