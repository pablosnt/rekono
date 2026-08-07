"""Serializers of the execution endpoints."""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from executions.models import Execution
from tools.serializers import ConfigurationSerializer


class ExecutionSerializer(ModelSerializer):
    """Serializer of an execution, including its output and its findings.

    Attributes:
        configuration: Tool configuration that the execution runs.
        has_report: Whether the tool wrote a report that can be downloaded.
    """

    configuration = ConfigurationSerializer(many=False, read_only=True)
    has_report = SerializerMethodField()

    class Meta:
        """Serializer configuration for the executions."""

        model = Execution
        fields = (
            "id",
            "task",
            "configuration",
            "output_plain",
            "executed_command",
            "skipped_reason",
            "has_report",
            "status",
            "start",
            "end",
            "defectdojo_test_id",
            "osint",
            "host",
            "port",
            "path",
            "technology",
            "credential",
            "vulnerability",
            "exploit",
        )

    def get_has_report(self, instance: Execution) -> bool:
        """Check if the execution has a report file that can be downloaded.

        Args:
            instance: Execution being serialized.

        Returns:
            Whether the tool wrote a report file. Only some tools write one, so an
            execution can be completed and still have no report to download.
        """
        return instance.output_file is not None


class SimpleExecutionSerializer(ModelSerializer):
    """Serializer with the minimum data needed to reference an execution.

    Attributes:
        configuration: Tool configuration that the execution runs.
    """

    configuration = ConfigurationSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration for the execution references."""

        model = Execution
        fields = ("id", "task", "configuration", "status", "start", "end", "defectdojo_test_id")
