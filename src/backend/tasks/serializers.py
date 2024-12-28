import math
from typing import Any, cast

from django.core.exceptions import ValidationError
from executions.enums import Status
from processes.models import Process
from processes.serializers import SimpleProcessSerializer
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)
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
    status = SerializerMethodField(read_only=True)
    progress = SerializerMethodField(read_only=True)

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
            "repeat_in",
            "repeat_time_unit",
            "creation",
            "enqueued_at",
            "start",
            "end",
            "wordlists",
            "input_technologies",
            "input_vulnerabilities",
            "executions",
            "notes",
            "reports",
            "status",
            "progress",
        )
        read_only_fields = (
            "executor",
            "creation",
            "enqueued_at",
            "start",
            "end",
            "executions",
            "notes",
            "reports",
            "status",
            "progress",
        )

    def get_status(self, instance: Any) -> Status:
        for status in [Status.RUNNING, Status.CANCELLED, Status.ERROR]:
            if instance.executions.filter(status=status).count() > 0:
                return status
        if (
            instance.executions.exclude(
                status__in=[Status.COMPLETED, Status.SKIPPED]
            ).count()
            == 0
        ):
            return Status.COMPLETED
        if instance.executions.filter(status=Status.SKIPPED).count() > 0:
            return Status.SKIPPED
        return Status.REQUESTED

    def get_progress(self, instance: Any) -> int | None:
        total = instance.executions.count()
        return (
            math.ceil(
                (
                    instance.executions.filter(
                        status__in=[
                            Status.ERROR,
                            Status.COMPLETED,
                            Status.SKIPPED,
                            Status.CANCELLED,
                        ]
                    ).count()
                    / total
                )
                * 100
            )
            if total > 0
            else 0
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("intensity"):
            attrs["intensity"] = IntensityEnum.NORMAL
        if attrs.get("configuration"):
            attrs["process"] = None
            if not Intensity.objects.filter(
                tool=cast(Configuration, attrs.get("configuration")).tool,
                value=attrs.get("intensity"),
            ).exists():
                raise ValidationError(
                    f'Invalid intensity {attrs["intensity"]} for tool {cast(Configuration, attrs.get("configuration")).tool.name}',
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
        if not attrs.get("repeat_in") or not attrs.get("repeat_time_unit"):
            attrs["repeat_in"] = None
            attrs["repeat_time_unit"] = None
        return super().validate(attrs)

    def create(self, validated_data: dict[str, Any]) -> Task:
        """Create instance from validated data.

        Args:
            validated_data (dict[str, Any]): Validated data

        Returns:
            Task: Created instance
        """
        task = super().create(validated_data)
        TasksQueue().enqueue(task)
        return task
