"""Django REST framework serializers for execution models.

This module provides serialization and deserialization capabilities for
execution records, including detailed and simplified views of execution
data for API consumption.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from executions.models import Execution
from tools.serializers import ConfigurationSerializer


class ExecutionSerializer(ModelSerializer):
    """Serializer for Execution model with detailed information.

    This serializer provides comprehensive serialization of execution
    records, including nested configuration data and computed fields
    for API responses.

    Attributes:
        configuration (ConfigurationSerializer): Nested serializer for
            tool configuration details.
        has_report (SerializerMethodField): Computed field indicating
            if the execution has an output report file.
    """

    configuration = ConfigurationSerializer(many=False, read_only=True)
    has_report = SerializerMethodField()

    class Meta:
        """Meta configuration for the ExecutionSerializer.

        Attributes:
            model: The Execution model to serialize.
            fields: Tuple of field names to include in serialization.
        """

        model = Execution
        fields = (
            "id",
            "task",
            "configuration",
            "output_plain",
            "skipped_reason",
            "has_report",
            "status",
            "start",
            "end",
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
        """Check if the execution has an output report file.

        Args:
            instance: The execution instance to check.

        Returns:
            bool: True if the execution has an output file, False otherwise.
        """
        return instance.output_file is not None


class SimpleExecutionSerializer(ModelSerializer):
    """Simplified serializer for Execution model.

    This serializer provides a minimal view of execution records,
    including only essential fields for list views and basic
    information display.

    Attributes:
        configuration (ConfigurationSerializer): Nested serializer for
            tool configuration details.
    """

    configuration = ConfigurationSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for the SimpleExecutionSerializer.

        Attributes:
            model: The Execution model to serialize.
            fields: Tuple of field names to include in serialization.
        """

        model = Execution
        fields = ("id", "task", "configuration", "status", "start", "end")
