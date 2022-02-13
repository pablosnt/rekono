from typing import Any, Dict

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
    '''Serializer to manage tasks via API.'''

    target = SimplyTargetSerializer(many=False, read_only=True)                 # Target details for read operations
    target_id = serializers.PrimaryKeyRelatedField(                             # Target Id for Task creation
        write_only=True,
        required=True,
        source='target',
        queryset=Target.objects.all()
    )
    process = SimplyProcessSerializer(many=False, read_only=True)               # Process details for read operations
    process_id = serializers.PrimaryKeyRelatedField(                            # Process Id for Task creation
        write_only=True,
        required=False,
        source='process',
        queryset=Process.objects.all()
    )
    tool = SimplyToolSerializer(many=False, read_only=True)                     # Tool details for read operations
    tool_id = serializers.PrimaryKeyRelatedField(                               # Tool Id for Task creation
        write_only=True,
        required=False,
        source='tool',
        queryset=Tool.objects.all()
    )
    # Configuration details for read operations
    configuration = ConfigurationSerializer(many=False, read_only=True)
    configuration_id = serializers.PrimaryKeyRelatedField(                      # Configuration Id for Task creation
        write_only=True,
        required=False,
        source='configuration',
        queryset=Configuration.objects.all()
    )
    # Intensity value to apply in task execution. By default, Normal
    intensity_rank = IntensityField(source='intensity', required=False)
    executor = SimplyUserSerializer(many=False, read_only=True)                 # Executor details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Task
        fields = (                                                              # Task fields exposed via API
            'id', 'target', 'target_id', 'process', 'process_id', 'tool', 'tool_id',
            'configuration', 'configuration_id', 'intensity_rank', 'executor', 'status',
            'scheduled_at', 'scheduled_in', 'scheduled_time_unit', 'repeat_in', 'repeat_time_unit',
            'start', 'end', 'wordlists', 'executions'
        )
        read_only_fields = ('executor', 'status', 'start', 'end', 'executions')                     # Read only fields

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        if not attrs.get('intensity'):                                          # Intensity doesn't exist
            attrs['intensity'] = IntensityRank.NORMAL                           # Normal intensity by default
        if attrs.get('tool'):                                                   # Tool task
            attrs['process'] = None
            if not attrs.get('configuration'):                                  # Configuration doesn't exist
                # Get default configuration for this tool
                attrs['configuration'] = Configuration.objects.filter(tool=attrs.get('tool'), default=True).first()
            # Get intensity for this tool
            intensity = Intensity.objects.filter(tool=attrs.get('tool'), value=attrs.get('intensity'))
            if not intensity:                                                   # Intensity not found for this tool
                raise serializers.ValidationError(
                    {'intensity': f'Invalid intensity {attrs["intensity"]} for tool {attrs["tool"].name}'}
                )
        elif attrs.get('process'):                                              # Process task
            attrs['tool'] = None
            attrs['configuration'] = None
        else:                                                                   # Tool or Process are required
            raise serializers.ValidationError({
                'tool': 'Invalid task. Process or tool is required',
                'process': 'Invalid task. Process or tool is required'
            })
        # Scheduled tasks only can be at future dates
        if attrs.get('scheduled_at') and attrs.get('scheduled_at') <= timezone.now():
            raise serializers.ValidationError({'scheduled_at': 'Scheduled datetime must be future'})
        for field, unit in [('scheduled_in', 'scheduled_time_unit'), ('repeat_in', 'repeat_time_unit')]:
            # Time and unit fields sanitization
            if not attrs.get(field):                                            # Time field doesn't exist
                attrs[unit] = None
            elif attrs.get(field) and not attrs.get(unit):                      # Unit field doesn't exist
                attrs[field] = None
        return super().validate(attrs)

    def create(self, validated_data: Dict[str, Any]) -> Task:
        '''Create instance from validated data.

        Args:
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Task: Created instance
        '''
        task = super().create(validated_data)                                   # Create task entity
        producer(task)                                                          # Enqueue task in tasks queue
        return task
