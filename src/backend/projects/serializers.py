from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.serializers import IntegerField, Serializer
from taggit.serializers import TaggitSerializer

from alerts.enums import AlertItem, AlertMode
from alerts.models import Alert
from framework.fields import TagField
from framework.serializers import RelatedNotesSerializer
from platforms.defectdojo.serializers import DefectDojoSyncSerializer
from projects.models import Project
from targets.serializers import SimpleTargetSerializer
from users.models import User
from users.serializers import SimpleUserSerializer


class ProjectSerializer(TaggitSerializer, RelatedNotesSerializer):
    targets = SimpleTargetSerializer(read_only=True, many=True)
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()  # Tags
    defectdojo_sync = DefectDojoSyncSerializer(many=False, read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "targets",
            "members",
            "tags",
            "defectdojo_sync",
            "notes",
        )
        read_only_fields = (
            "owner",
            "targets",
            "members",
            "defectdojo_sync",
            "notes",
        )

    @transaction.atomic()
    def create(self, validated_data: dict[str, Any]) -> Project:
        project = super().create(validated_data)
        # Add project owner also in member list
        project.members.add(validated_data.get("owner"))
        # Create trending CVE monitor alert by default
        alert = Alert.objects.create(
            project=project,
            item=AlertItem.CVE,
            mode=AlertMode.MONITOR,
            enabled=True,
            owner=None,
        )
        alert.subscribers.add(validated_data.get("owner"))
        return project
