from executions.models import Execution
from processes.serializers import StepSerializer
from rest_framework import serializers


class ExecutionSerializer(serializers.ModelSerializer):
    step = StepSerializer(many=False, read_only=True)

    class Meta:
        model = Execution
        fields = (
            'id', 'task', 'step', 'output_plain', 'output_error', 'status', 'start', 'end',
            'reported_to_defectdojo', 'osint', 'host', 'enumeration', 'endpoint', 'technology',
            'vulnerability', 'credential', 'exploit'
        )
