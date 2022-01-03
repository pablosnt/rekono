from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from processes.models import Process
from processes.serializers import SimplyProcessSerializer
from rest_framework import serializers
from targets.models import Target
from targets.serializers import SimplyTargetSerializer
from tasks.models import Task
from tasks.queue import producer
from tools.enums import IntensityRank
from tools.models import Configuration, Intensity, Tool
from tools.serializers import (ConfigurationSerializer, IntensityField,
                               SimplyToolSerializer)
from users.serializers import SimplyUserSerializer


class TaskSerializer(serializers.ModelSerializer):
    target = SimplyTargetSerializer(many=False, read_only=True)
    target_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=True,
        source='target',
        queryset=Target.objects.all()
    )
    process = SimplyProcessSerializer(many=False, read_only=True)
    process_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=False,
        source='process',
        queryset=Process.objects.all()
    )
    tool = SimplyToolSerializer(many=False, read_only=True)
    tool_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=False,
        source='tool',
        queryset=Tool.objects.all()
    )
    configuration = ConfigurationSerializer(many=False, read_only=True)
    configuration_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=False,
        source='configuration',
        queryset=Configuration.objects.all()
    )
    intensity_rank = IntensityField(source='intensity', required=False)
    executor = SimplyUserSerializer(many=False, read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'target', 'target_id', 'process', 'process_id', 'tool',
            'tool_id', 'configuration', 'configuration_id',
            'intensity_rank', 'executor', 'status', 'scheduled_at',
            'scheduled_in', 'scheduled_time_unit', 'repeat_in',
            'repeat_time_unit', 'start', 'end', 'wordlists', 'executions'
        )
        read_only_fields = ('executor', 'status', 'start', 'end', 'executions')

    def validate(self, attrs):
        if not attrs.get('process') and not attrs.get('tool'):
            raise serializers.ValidationError(
                {
                    'tool': 'Invalid task. Process or tool is required',
                    'process': 'Invalid task. Process or tool is required'
                }
            )
        if attrs.get('scheduled_at') and attrs.get('scheduled_at') <= timezone.now():
            raise serializers.ValidationError({'scheduled_at': 'Scheduled datetime must be future'})
        for field, unit in [
            ('scheduled_in', 'scheduled_time_unit'),
            ('repeat_in', 'repeat_time_unit')
        ]:
            if not attrs.get(field):
                attrs[unit] = None
            elif attrs.get(field) and not attrs.get(unit):
                attrs[field] = None
        if not attrs.get('intensity'):
            attrs['intensity'] = IntensityRank.NORMAL.value
        if attrs.get('tool'):
            attrs['process'] = None
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
                raise serializers.ValidationError(
                    {'intensity': f'Invalid intensity {attrs.get("intensity")} for tool {attrs.get("tool").name}'}      # noqa: E501
                )
        return super().validate(attrs)

    def create(self, validated_data):
        task = super().create(validated_data)
        rekono_address = None
        if self.context.get('request'):
            rekono_address = get_current_site(self.context.get('request')).domain
        producer(task, rekono_address)
        return task
