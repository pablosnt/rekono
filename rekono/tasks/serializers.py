from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from tasks.enums import TimeUnit
from tasks.models import Parameter, Task
from tasks.queue import producer
from tools.enums import IntensityRank
from tools.models import Intensity


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = ('key', 'value')
        ordering = ['-id']


class TaskSerializer(serializers.ModelSerializer):
    parameters = ParameterSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Task
        fields = (
            'id', 'target', 'process', 'tool', 'configuration',
            'intensity', 'executor', 'status', 'scheduled_at',
            'scheduled_in', 'scheduled_time_unit', 'repeat_in',
            'repeat_time_unit', 'start', 'end', 'parameters', 'executions'
        )
        read_only_fields = ('executor', 'status', 'start', 'end', 'executions')
        ordering = ['-id']

    def validate(self, attrs):
        if attrs.get('scheduled_at') and attrs.get('scheduled_at') <= timezone.now():
            raise serializers.ValidationError({'scheduled_at': 'Scheduled datetime must be future'})
        if not attrs.get('scheduled_in'):
            attrs['scheduled_time_unit'] = None
        if not attrs.get('repeat_in'):
            attrs['repeat_time_unit'] = None
        if attrs.get('scheduled_in') and not attrs.get('scheduled_time_unit'):
            attrs['scheduled_in'] = None
        if attrs.get('repeat_in') and not attrs.get('repeat_time_unit'):
            attrs['repeat_in'] = None
        if not attrs.get('process') and not attrs.get('tool'):
            raise serializers.ValidationError(
                {
                    'tool': 'Invalid task. Process or tool is required',
                    'process': 'Invalid task. Process or tool is required'
                }
            )
        if attrs.get('tool'):
            intensity = Intensity.objects.filter(
                tool=attrs.get('tool'),
                value=attrs.get('intensity')
            )
            if not intensity:
                intensity = IntensityRank(attrs.get('intensity')).name
                tool = attrs.get('tool').name
                raise serializers.ValidationError(
                    {'intensity': f'Invalid intensity {intensity} for tool {tool}'}
                )
        return super().validate(attrs)

    def create(self, validated_data):
        scheduled_time_unit = TimeUnit(validated_data.get('scheduled_time_unit')) if validated_data.get('scheduled_time_unit') else None
        repeat_time_unit = TimeUnit(validated_data.get('repeat_time_unit')) if validated_data.get('repeat_time_unit') else None
        task = Task.objects.create(
            target=validated_data.get('target'),
            process=validated_data.get('process'),
            tool=validated_data.get('tool'),
            configuration=validated_data.get('configuration'),
            intensity=validated_data.get('intensity'),
            executor=validated_data.get('executor'),
            scheduled_at=validated_data.get('scheduled_at'),
            scheduled_in=validated_data.get('scheduled_in'),
            scheduled_time_unit=scheduled_time_unit,
            repeat_in=validated_data.get('repeat_in'),
            repeat_time_unit=repeat_time_unit
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
        producer(task, parameters, get_current_site(self.context.get('request')).domain)
        return task
