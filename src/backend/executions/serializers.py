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
            "group",
            "configuration",
            "output_plain",
            "output_error",
            "skipped_reason",
            "has_report",
            "status",
            "start",
            "end",
        )

    def get_has_report(self, instance: Execution) -> bool:
        return instance.output_file is not None
