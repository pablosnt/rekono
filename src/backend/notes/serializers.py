from typing import Any, Dict

from framework.fields import TagField
from framework.serializers import LikeSerializer
from notes.models import Note
from projects.models import Project
from projects.serializers import ProjectSerializer
from rest_framework.serializers import PrimaryKeyRelatedField, SerializerMethodField
from taggit.serializers import TaggitSerializer
from targets.models import Target
from targets.serializers import SimpleTargetSerializer
from users.serializers import SimpleUserSerializer


class NoteSerializer(TaggitSerializer, LikeSerializer):
    project = ProjectSerializer(many=False, read_only=True, required=False)
    project_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        source="project",
        queryset=Project.objects.all(),
    )
    target = SimpleTargetSerializer(many=False, read_only=True, required=False)
    target_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        source="target",
        queryset=Target.objects.all(),
    )
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()
    forked = SerializerMethodField(read_only=True)

    class Meta:
        model = Note
        fields = (
            "id",
            "project",
            "project_id",
            "target",
            "target_id",
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
        if attrs.get("target"):
            attrs["project"] = None
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
