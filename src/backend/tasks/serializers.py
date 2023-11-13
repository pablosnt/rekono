from typing import Any, Dict

from django.core.exceptions import ValidationError
from executions.serializers import ExecutionSerializer
from processes.serializers import SimpleProcessSerializer
from rest_framework.serializers import ModelSerializer
from targets.serializers import SimpleTargetSerializer
from tasks.models import Task
from tasks.queues import TasksQueue
from tools.enums import Intensity as IntensityEnum
from tools.fields import IntegerChoicesField
from tools.models import Intensity
from tools.serializers import ConfigurationSerializer
from users.serializers import SimpleUserSerializer
from wordlists.serializers import WordlistSerializer


class TaskSerializer(ModelSerializer):
    """Serializer to manage tasks via API."""

    # TODO: return proper data, and expect just an ID
    # target = SimpleTargetSerializer(many=False)
    # process = SimpleProcessSerializer(many=False)
    # configuration = ConfigurationSerializer(many=False)
    intensity = IntegerChoicesField(model=IntensityEnum, required=False)
    executor = SimpleUserSerializer(many=False, read_only=True)
    # wordlists = WordlistSerializer(many=False, required=False)
    executions = ExecutionSerializer(many=False, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "target",
            "process",
            "configuration",
            "intensity",
            "executor",
            "scheduled_at",
            "scheduled_in",
            "scheduled_time_unit",
            "repeat_in",
            "repeat_time_unit",
            "creation",
            "enqueued_at",
            "start",
            "end",
            "wordlists",
            "executions",
        )
        read_only_fields = (
            "executor",
            "creation",
            "enqueued_at",
            "start",
            "end",
            "wordlists",
            "executions",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if not attrs.get("intensity"):
            attrs["intensity"] = IntensityEnum.NORMAL
        if attrs.get("configuration"):
            attrs["process"] = None
            if not Intensity.objects.filter(
                tool=attrs.get("configuration").tool, value=attrs.get("intensity")
            ).exists():
                raise ValidationError(
                    f'Invalid intensity {attrs["intensity"]} for tool {attrs["tool"].name}',
                    code="intensity",
                )
        elif attrs.get("process"):
            attrs["configuration"] = None
        else:
            raise ValidationError(
                {
                    "configuration": "Invalid task. Process or configuration is required",
                    "process": "Invalid task. Process or configuration is required",
                }
            )
        for field, unit in [
            ("scheduled_in", "scheduled_time_unit"),
            ("repeat_in", "repeat_time_unit"),
        ]:
            if not attrs.get(field) or not attrs.get(unit):
                attrs[field] = None
                attrs[unit] = None
        return super().validate(attrs)

    def create(self, validated_data: Dict[str, Any]) -> Task:
        """Create instance from validated data.

        Args:
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Task: Created instance
        """
        task = super().create(validated_data)
        # TODO: Fix enqueue errors
        # TasksQueue().enqueue(task)
        return task
