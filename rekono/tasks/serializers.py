from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from rest_framework import serializers
from tasks.enums import TimeUnit
from tasks.models import Parameter, Task
from tasks.queue import producer
from tools.enums import IntensityRank
from tools.models import Configuration, Intensity


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = ('key', 'value')


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
        if attrs.get('scheduled_time_unit'):
            attrs['scheduled_time_unit'] = TimeUnit(attrs.get('scheduled_time_unit'))
        if attrs.get('repeat_time_unit'):
            attrs['repeat_time_unit'] = TimeUnit(attrs.get('repeat_time_unit'))
        if not attrs.get('process') and not attrs.get('tool'):
            raise serializers.ValidationError(
                {
                    'tool': 'Invalid task. Process or tool is required',
                    'process': 'Invalid task. Process or tool is required'
                }
            )
        if not attrs.get('intensity'):
            attrs['intensity'] = IntensityRank.NORMAL
        if attrs.get('tool'):
            if not attrs.get('configuration'):
                attrs['configuration'] = Configuration.objects.filter(
                    tool=attrs.get('tool'),
                    default=True
                ).first()
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
        task = Task.objects.create(
            target=validated_data.get('target'),
            process=validated_data.get('process'),
            tool=validated_data.get('tool'),
            configuration=validated_data.get('configuration'),
            intensity=validated_data.get('intensity'),
            executor=validated_data.get('executor'),
            scheduled_at=validated_data.get('scheduled_at'),
            scheduled_in=validated_data.get('scheduled_in'),
            scheduled_time_unit=validated_data.get('scheduled_time_unit'),
            repeat_in=validated_data.get('repeat_in'),
            repeat_time_unit=validated_data.get('scheduledrepeat_time_unit_time_unit'),
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
        domain = get_current_site(self.context.get('request')).domain if self.context.get('request') else None
        producer(task, parameters, domain)
        return task
