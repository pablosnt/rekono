from executions.models import Execution
from tools.enums import IntensityRank
from tools.models import Intensity
from executions.exceptions import InvalidRequestException
from executions.models import Parameter, Request
from rest_framework import serializers
from queues.requests import producer


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = ('key', 'value')


class ExecutionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Execution
        fields = (
            'id', 'request', 'step', 'output_plain', 'output_error', 'status', 'start', 'end',
            'osints', 'hosts', 'enumerations', 'http_endpoints', 'technologies',
            'vulnerabilities', 'exploits'
        )
    

class RequestSerializer(serializers.ModelSerializer):
    parameters = ParameterSerializer(read_only=False, many=True, required=False)
    intensity = serializers.CharField(source='get_intensity_display')
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Request
        fields = (
            'id', 'target', 'process', 'tool', 'configuration',
            'intensity', 'executor', 'status', 'start', 'end',
            'parameters', 'executions'
        )
        read_only_fields = ('executor', 'status', 'start', 'end', 'executions')

    def validate(self, attrs):
        if not attrs.get('process') and not attrs.get('tool'):
            raise InvalidRequestException('Invalid request. Process or tool is required')
        if attrs.get('tool'):
            intensity = Intensity.objects.filter(
                tool=attrs.get('tool'),
                value=attrs.get('get_intensity_display')
            )
            if not intensity:
                intensity = IntensityRank(attrs.get('get_intensity_display')).name
                tool = attrs.get('tool').name
                raise InvalidRequestException(f'Invalid intensity {intensity} for tool {tool}')
        return super().validate(attrs)

    def create(self, validated_data):
        request = Request.objects.create(
            target=validated_data.get('target'),
            process=validated_data.get('process'),
            tool=validated_data.get('tool'),
            configuration=validated_data.get('configuration'),
            intensity=validated_data.get('get_intensity_display'),
            executor=validated_data.get('executor')
        )
        parameters = []
        if 'parameters' in validated_data:
            parameters_data = validated_data.pop('parameters')
            for parameter in parameters_data:
                parameter['request'] = request
                parameters.append(
                    ParameterSerializer().create(
                        validated_data=parameter
                    )
                )
        producer.process_request(request, parameters)
        return request
