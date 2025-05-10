from typing import Any, cast

from framework.fields import TagField
from framework.models import BaseModel
from framework.serializers import LikeSerializer
from notes.models import Note
from rest_framework.fields import ValidationError
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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        data_links = [link for link in reversed(links) if attrs.get(link)]
        if len(data_links) > 0:
            for value in [link for link in links if link != data_links[0]]:
                attrs[value] = None
            attrs["project"] = cast(BaseModel, attrs.get(data_links[0])).get_project()
        if not attrs.get("project"):
            raise ValidationError("A relationship with a project entity is needed", code="project")
        return attrs

    def update(self, instance: Note, validated_data: dict[str, Any]) -> Note:
        unlink_forks = instance.public and not validated_data.get("public", False)
        if instance.forked_from and validated_data.get("public", False):
            validated_data["public"] = True
        new_instance = super().update(instance, validated_data)
        if unlink_forks:
            Note.objects.filter(public=False, forked_from=instance).update(forked_from=None)
        return new_instance
