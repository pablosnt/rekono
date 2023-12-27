from executions.models import Execution
from rest_framework.serializers import ModelSerializer
from tools.serializers import ConfigurationSerializer


class ExecutionSerializer(ModelSerializer):
    configuration = ConfigurationSerializer(many=False, read_only=True)

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
            "status",
            "start",
            "end",
        )
