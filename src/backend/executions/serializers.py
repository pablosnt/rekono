from executions.models import Execution
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from tools.serializers import ConfigurationSerializer


class ExecutionSerializer(ModelSerializer):
    configuration = ConfigurationSerializer(many=False, read_only=True)
    has_report = SerializerMethodField()

    class Meta:
        model = Execution
        fields = (
            "id",
            "task",
            "configuration",
            "output_plain",
            "output_error",
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
        return instance.output_file is not None


class SimpleExecutionSerializer(ModelSerializer):
    configuration = ConfigurationSerializer(many=False, read_only=True)

    class Meta:
        model = Execution
        fields = ("id", "task", "configuration", "status", "start", "end")
