from executions.models import Execution
from tools.enums import IntensityRank
from tools.models import Intensity
from executions.exceptions import InvalidTaskException
from executions.models import Parameter, Task
from rest_framework import serializers
from queues.tasks import producer


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = ('key', 'value')


class ExecutionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Execution
        fields = (
            'id', 'task', 'step', 'output_plain', 'output_error', 'status', 'start', 'end',
            'osints', 'hosts', 'enumerations', 'http_endpoints', 'technologies',
            'vulnerabilities', 'exploits'
        )
    

class TaskSerializer(serializers.ModelSerializer):
    parameters = ParameterSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Task
        fields = (
            'id', 'target', 'process', 'tool', 'configuration',
            'intensity', 'executor', 'status', 'start', 'end',
            'parameters', 'executions'
        )
        read_only_fields = ('executor', 'status', 'start', 'end', 'executions')

    def validate(self, attrs):
        if not attrs.get('process') and not attrs.get('tool'):
            raise InvalidTaskException('Invalid task. Process or tool is required')
        if attrs.get('tool'):
            intensity = Intensity.objects.filter(
                tool=attrs.get('tool'),
                value=attrs.get('intensity')
            )
            if not intensity:
                intensity = IntensityRank(attrs.get('intensity')).name
                tool = attrs.get('tool').name
                raise InvalidTaskException(f'Invalid intensity {intensity} for tool {tool}')
        return super().validate(attrs)

    def create(self, validated_data):
        task = Task.objects.create(
            target=validated_data.get('target'),
            process=validated_data.get('process'),
            tool=validated_data.get('tool'),
            configuration=validated_data.get('configuration'),
            intensity=validated_data.get('intensity'),
            executor=validated_data.get('executor')
        )
        parameters = []
        if 'parameters' in validated_data:
            parameters_data = validated_data.pop('parameters')
            for parameter in parameters_data:
                parameter['task'] = task
                parameters.append(
                    ParameterSerializer().create(
                        validated_data=parameter
                    )
                )
        producer.process_task(task, parameters)
        return task
