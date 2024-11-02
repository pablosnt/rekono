from typing import Any

from projects.models import Project
from rest_framework.serializers import IntegerField, PrimaryKeyRelatedField, Serializer
from targets.models import Target


class ScopeSerializer(Serializer):
    project = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, queryset=Project.objects.all()
    )
    target = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, queryset=Target.objects.all()
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs.get("target"):
            attrs["project"] = None
        return super().validate(attrs)


class TimelineSerializer(Serializer):
    months = IntegerField(max_value=24, min_value=1, required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("months"):
            attrs["months"] = 6
        return super().validate(attrs)


class ScopeTimelineSerializer(ScopeSerializer, TimelineSerializer):
    pass
