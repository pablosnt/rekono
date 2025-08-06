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
