from typing import Any, Dict

from framework.fields import TagField
from framework.serializers import LikeSerializer
from notes.models import Note
from rest_framework.serializers import SerializerMethodField
from taggit.serializers import TaggitSerializer
from users.serializers import SimpleUserSerializer

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
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()
    forked = SerializerMethodField(read_only=True)

    class Meta:
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
        return instance.forks.filter(owner=self.context.get("request").user).exists()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        link = [l for l in reversed(links) if attrs.get(l)]
        if len(link) > 0:
            for value in [l for l in links if l != link[0]]:
                attrs[value] = None
            attrs["project"] = attrs.get(link[0]).get_project()
        return attrs

    def update(self, instance: Note, validated_data: Dict[str, Any]) -> Note:
        unlink_forks = instance.public and validated_data.get("public", False) == False
        if instance.forked_from and validated_data.get("public", False) == True:
            validated_data["public"] = True
        new_instance = super().update(instance, validated_data)
        if unlink_forks:
            Note.objects.filter(public=False, forked_from=instance).update(
                forked_from=None
            )
        return new_instance
