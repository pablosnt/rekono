from typing import Any, Dict

from django.core.exceptions import ValidationError
from processes.models import Process
from processes.serializers import SimpleProcessSerializer
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from targets.models import Target
from targets.serializers import SimpleTargetSerializer
from tasks.models import Task
from tasks.queues import TasksQueue
from tools.enums import Intensity as IntensityEnum
from tools.fields import IntegerChoicesField
from tools.models import Configuration, Intensity
from tools.serializers import ConfigurationSerializer
from users.serializers import SimpleUserSerializer


class TaskSerializer(ModelSerializer):
    target_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=True,
        source="target",
        queryset=Target.objects.all(),
    )
    target = SimpleTargetSerializer(many=False, read_only=True)
    process_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        source="process",
        queryset=Process.objects.all(),
    )
    process = SimpleProcessSerializer(many=False, read_only=True)
    configuration_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        source="configuration",
        queryset=Configuration.objects.all(),
    )
    configuration = ConfigurationSerializer(many=False, read_only=True)
    intensity = IntegerChoicesField(model=IntensityEnum, required=False)
    executor = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "target_id",
            "target",
            "process_id",
            "process",
            "configuration_id",
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
                    f'Invalid intensity {attrs["intensity"]} for tool {attrs.get("configuration").tool.name}',
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
        TasksQueue().enqueue(task)
        return task
