"""Serializers of the task endpoints."""

import math
from typing import Any, cast

from django.core.exceptions import ValidationError
from rest_framework.serializers import PrimaryKeyRelatedField, SerializerMethodField

from executions.enums import Status
from framework.serializers import RelatedNotesSerializer
from input_types.enums import InputTypeName
from processes.models import Process
from processes.serializers import SimpleProcessSerializer
from target_ports.models import TargetPort
from target_ports.serializers import TargetPortSerializer
from targets.models import Target
from targets.serializers import SimpleTargetSerializer
from tasks.models import Task
from tasks.queues import TasksQueue
from tools.enums import Intensity as IntensityEnum
from tools.fields import IntegerChoicesField
from tools.models import Configuration, Input, Intensity
from tools.serializers import ConfigurationSerializer
from users.serializers import SimpleUserSerializer


class TaskSerializer(RelatedNotesSerializer):
    """Serializer of a task, which also enqueues it when it's created.

    Attributes:
        target_id: Target to be scanned.
        target: Data of that target.
        process_id: Process to be executed, if the task doesn't run one single
          configuration.
        process: Data of that process.
        configuration_id: Tool configuration to be executed, if the task doesn't run
          a process.
        configuration: Data of that configuration.
        target_port_id: Port that the scan is limited to, if there is one.
        target_port: Data of that target port.
        intensity: How aggressive the executions of the task are.
        executor: User that created the task.
        status: Status of the task, calculated from the status of its executions.
        progress: Percentage of the executions of the task that already finished.
    """

    target_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=True, source="target", queryset=Target.objects.all()
    )
    target = SimpleTargetSerializer(many=False, read_only=True)
    process_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, source="process", queryset=Process.objects.all()
    )
    process = SimpleProcessSerializer(many=False, read_only=True)
    configuration_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, source="configuration", queryset=Configuration.objects.all()
    )
    configuration = ConfigurationSerializer(many=False, read_only=True)
    target_port_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, source="target_port", queryset=TargetPort.objects.all()
    )
    target_port = TargetPortSerializer(many=False, read_only=True)
    intensity = IntegerChoicesField(model=IntensityEnum, required=False)
    executor = SimpleUserSerializer(many=False, read_only=True)
    status = SerializerMethodField(read_only=True)
    progress = SerializerMethodField(read_only=True)

    class Meta:
        """Serializer configuration for the tasks."""

        model = Task
        fields = (
            "id",
            "target_id",
            "target",
            "process_id",
            "process",
            "configuration_id",
            "configuration",
            "target_port_id",
            "target_port",
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

    def get_status(self, instance: Any) -> str:
        """Get the status of the task, derived from the status of its executions.

        Any RUNNING, CANCELLED, or ERROR execution takes priority and becomes the
        task status. If every execution finished as COMPLETED or SKIPPED, the task
        is COMPLETED. A task without executions is CANCELLED once it has ended, or
        REQUESTED while still pending. A mix of finished and still-REQUESTED
        executions is reported as RUNNING.

        Args:
            instance: Task being serialized.

        Returns:
            The status of the task.
        """
        for status in [Status.RUNNING, Status.CANCELLED, Status.ERROR]:
            if instance.executions.filter(status=status).exists():
                return status
        if (
            instance.executions.count() > 0
            and instance.executions.exclude(status__in=[Status.COMPLETED, Status.SKIPPED]).count() == 0
        ):
            return Status.COMPLETED
        if instance.executions.count() == 0 and instance.end:
            return Status.CANCELLED
        if instance.executions.exclude(status=Status.REQUESTED).exists():
            return Status.RUNNING
        return Status.REQUESTED

    def get_progress(self, instance: Any) -> int:
        """Get the percentage of the executions of the task that already finished.

        A task without executions is at 100 when it already ended, and at 0 while
        it's still pending.

        Args:
            instance: Task being serialized.

        Returns:
            The progress as a percentage between 0 and 100.
        """
        total = instance.executions.count()
        return (
            math.ceil((instance.executions.filter(status__in=Status.finished()).count() / total) * 100)
            if total > 0
            else (100 if instance.end else 0)
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check that the task can be executed, and complete its missing data.

        A task must reference either a process or a configuration. If both are
        given, the configuration wins and the process is discarded rather than
        rejected. The inputs that the selected tool doesn't accept are dropped
        instead of being rejected too, and the repetition is cleared unless both of
        its fields are provided.

        Args:
            attrs: Task fields sent by the user.

        Returns:
            The validated data, with the default intensity applied and the values
            that this task can't use already removed.

        Raises:
            ValidationError: If neither a process nor a configuration is provided,
              if the configuration is deprecated or doesn't support the requested
              intensity, or if the target port belongs to another target.
        """
        if not attrs.get("intensity"):
            attrs["intensity"] = IntensityEnum.NORMAL
        target = attrs.get("target")
        target_port = attrs.get("target_port")
        if target_port and target and target_port.target_id != target.id:
            raise ValidationError("The target port doesn't belong to the task target", code="target_port")
        if attrs.get("configuration"):
            if cast(Configuration, attrs.get("configuration")).deprecated:
                raise ValidationError("Deprecated configurations can't be executed", code="configuration")
            attrs["process"] = None
            if not Intensity.objects.filter(
                tool=cast(Configuration, attrs.get("configuration")).tool, value=attrs.get("intensity")
            ).exists():
                raise ValidationError(
                    f"Invalid intensity {attrs['intensity']} for tool {cast(Configuration, attrs.get('configuration')).tool.name}",
                    code="intensity",
                )
            for input_type, field in [
                (InputTypeName.TECHNOLOGY, "input_technologies"),
                (InputTypeName.VULNERABILITY, "input_vulnerabilities"),
            ]:
                if len(attrs.get(field, [])) > 0 and not Input.objects.filter(
                    argument__configuration=attrs.get("configuration"), type__name=input_type
                ):
                    attrs[field] = []
        elif attrs.get("process"):
            attrs["configuration"] = None
            attrs["input_technologies"] = []
            attrs["input_vulnerabilities"] = []
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
        """Create the task and enqueue it, so it starts without any extra request.

        Args:
            validated_data: Task fields, already validated.

        Returns:
            The created task, already enqueued.
        """
        task = super().create(validated_data)
        TasksQueue().enqueue(task)
        return task
