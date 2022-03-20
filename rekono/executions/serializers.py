from executions.models import Execution
from processes.serializers import StepSerializer
from rest_framework import serializers


class ExecutionSerializer(serializers.ModelSerializer):
    '''Serializer to get the executions data via API.'''

    step = StepSerializer(many=False, read_only=True)                           # Step details

    class Meta:
        '''Serializer metadata.'''

        model = Execution
        fields = (                                                              # Execution fields exposed via API
            'id', 'task', 'step', 'output_plain', 'output_error', 'status', 'start', 'end',
            'reported_to_defectdojo', 'osint', 'host', 'port', 'path', 'technology',
            'vulnerability', 'credential', 'exploit'
        )
