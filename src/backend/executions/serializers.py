from executions.models import Execution
from rest_framework import serializers
from tools.serializers import ConfigurationSerializer, SimplyToolSerializer


class ExecutionSerializer(serializers.ModelSerializer):
    '''Serializer to get the executions data via API.'''

    tool = SimplyToolSerializer(many=False, read_only=True)                     # Tool details
    configuration = ConfigurationSerializer(many=False, read_only=True)         # Configuration details

    class Meta:
        '''Serializer metadata.'''

        model = Execution
        fields = (                                                              # Execution fields exposed via API
            'id', 'task', 'tool', 'configuration', 'output_plain', 'output_error',
            'status', 'start', 'end', 'imported_in_defectdojo', 'osint', 'host',
            'port', 'path', 'technology', 'vulnerability', 'credential', 'exploit'
        )
