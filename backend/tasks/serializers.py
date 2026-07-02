"""Django REST framework serializers for task models.

Provides serializer classes for task creation, validation, and conversion between
Django model instances and JSON data. Includes complex validation logic for
task configuration and automatic queue management.
"""

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
    """Serializer for Task model with comprehensive validation and computed fields.

    Handles serialization of Task instances including complex validation logic
    for mutually exclusive process/configuration fields, intensity validation,
    and automatic task queuing upon creation.

    Attributes:
        target_id (PrimaryKeyRelatedField): Target ID for task creation (write-only)
        target (SimpleTargetSerializer): Serialized target information (read-only)
        process_id (PrimaryKeyRelatedField): Process ID for multi-step tasks (write-only, optional)
        process (SimpleProcessSerializer): Serialized process information (read-only)
        configuration_id (PrimaryKeyRelatedField): Tool configuration ID for single-tool tasks (write-only, optional)
        configuration (ConfigurationSerializer): Serialized configuration information (read-only)
        target_port_id (PrimaryKeyRelatedField): Target port ID for task execution (write-only, optional)
        target_port (TargetPortSerializer): Serialized target port information (read-only)
        intensity (IntegerChoicesField): Execution intensity level
        executor (SimpleUserSerializer): Task creator information (read-only)
        status (SerializerMethodField): Computed task status based on execution states
        progress (SerializerMethodField): Computed progress percentage (0-100)
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
        """Meta configuration for the TaskSerializer.

        Attributes:
            model (Model): The Task model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified
        """

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
        """Get the computed status of the task based on execution states.

        Determines task status by analyzing the status of all associated executions.
        Follows priority: RUNNING > CANCELLED > ERROR > COMPLETED > REQUESTED

        Args:
            instance (Task): The task instance being serialized

        Returns:
            str: The computed task status
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
        """Get the completion progress percentage for the task.

        Calculates progress based on the ratio of completed executions
        (including ERROR, COMPLETED, SKIPPED, CANCELLED) to total executions.

        Args:
            instance (Task): The task instance being serialized

        Returns:
            int: Progress percentage from 0 to 100
        """
        total = instance.executions.count()
        return (
            math.ceil(
                (
                    instance.executions.filter(
                        status__in=[Status.ERROR, Status.COMPLETED, Status.SKIPPED, Status.CANCELLED]
                    ).count()
                    / total
                )
                * 100
            )
            if total > 0
            else (100 if instance.end else 0)
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate task configuration and ensure data consistency.

        Performs complex validation including:
        - Mutually exclusive process/configuration validation
        - Tool intensity compatibility checks
        - Input type validation for tool configurations
        - Repeat scheduling validation

        Args:
            attrs (dict[str, Any]): The attributes to validate

        Returns:
            dict[str, Any]: The validated attributes

        Raises:
            ValidationError: If validation fails for any reason
        """
        if not attrs.get("intensity"):
            attrs["intensity"] = IntensityEnum.NORMAL
        # Ensure the target port belongs to the task's target
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
        """Create a new task and automatically enqueue it for execution.

        Creates the task instance and immediately adds it to the task queue
        for processing. Handles both immediate and scheduled task execution.

        Args:
            validated_data (dict[str, Any]): The validated data for creating the task

        Returns:
            Task: The created Task instance
        """
        task = super().create(validated_data)
        TasksQueue().enqueue(task)
        return task
