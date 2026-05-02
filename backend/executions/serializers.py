"""Django REST framework serializers for execution models.

Provides serialization for execution records including detailed and simplified
views with nested configuration data and computed fields.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from executions.models import Execution
from tools.serializers import ConfigurationSerializer


class ExecutionSerializer(ModelSerializer):
    """Serializer for Execution model with detailed information.

    Provides comprehensive serialization including nested configuration data,
    finding relationships, and computed fields for API responses.

    Attributes:
        configuration (ConfigurationSerializer): Nested tool configuration details
        has_report (SerializerMethodField): Whether execution has output report file
    """

    configuration = ConfigurationSerializer(many=False, read_only=True)
    has_report = SerializerMethodField()

    class Meta:
        """Meta configuration for the ExecutionSerializer.

        Attributes:
            model (Model): The Execution model to serialize
            fields (tuple): Field names to include in serialization
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
        """Check if the execution has an output report file.

        Args:
            instance (Execution): The execution instance to check

        Returns:
            bool: True if execution has output file, False otherwise
        """
        return instance.output_file is not None


class SimpleExecutionSerializer(ModelSerializer):
    """Simplified serializer for Execution model.

    Provides minimal view of execution records with only essential fields
    for list views and basic information display.

    Attributes:
        configuration (ConfigurationSerializer): Nested tool configuration details
    """

    configuration = ConfigurationSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for the SimpleExecutionSerializer.

        Attributes:
            model (Model): The Execution model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = Execution
        fields = ("id", "task", "configuration", "status", "start", "end", "defectdojo_test_id")
