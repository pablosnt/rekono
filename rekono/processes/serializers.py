from typing import Any, Dict, List

from api.fields import RekonoTagField
from drf_spectacular.utils import extend_schema_field
from likes.serializers import LikeBaseSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from taggit.serializers import TaggitSerializer
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, SimplyToolSerializer
from users.serializers import SimplyUserSerializer

from processes.models import Process, Step


class StepPrioritySerializer(serializers.ModelSerializer):
    '''Serializer to update the step priority data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Step
        fields = ('id', 'process', 'tool', 'configuration', 'priority')         # Step fields exposed via API
        # All of them configured as read only except priority
        read_only_fields = ('id', 'process', 'tool', 'configuration')


class StepSerializer(serializers.ModelSerializer):
    '''Serializer to manage steps via API.'''

    tool = SimplyToolSerializer(read_only=True, many=False)                     # Tool details for read operations
    tool_id = serializers.PrimaryKeyRelatedField(                               # Tool Id for Step creation
        write_only=True,
        required=True,
        source='tool',
        queryset=Tool.objects.all()
    )
    # Configuration details for read operations
    configuration = ConfigurationSerializer(read_only=True, many=False)
    configuration_id = serializers.PrimaryKeyRelatedField(                      # Configuration Id for Step creation
        write_only=True,
        required=False,                                                         # If not present, default will be used
        source='configuration',
        queryset=Configuration.objects.all()
    )

    class Meta:
        '''Serializer metadata.'''

        model = Step
        # Step fields exposed via API
        fields = ('id', 'process', 'tool', 'tool_id', 'configuration', 'configuration_id', 'priority')

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)                                         # Super data validation
        configuration = attrs.get('configuration')
        if configuration:                                                       # Configuration present
            # Check if configuration is valid for the tool
            check_configuration = Configuration.objects.filter(tool=attrs.get('tool'), id=configuration.id).exists()
            if not bool(check_configuration):
                configuration = None                                            # Invalid configuration
        if not configuration:                                                   # Configuration not present
            # Get default configuration for the tool
            attrs['configuration'] = Configuration.objects.filter(tool=attrs.get('tool'), default=True).first()
        steps = Step.objects.filter(                                            # Check step unique constraint
            process=attrs.get('process'),
            tool=attrs.get('tool'),
            configuration=attrs.get('configuration')
        ).exists()
        if bool(steps):                                                         # Step already exists
            raise serializers.ValidationError(
                {'process': f'Invalid request. Process {attrs["process"].name} still has this step'}
            )
        return attrs


class ProcessSerializer(TaggitSerializer, serializers.ModelSerializer, LikeBaseSerializer):
    '''Serializer to manage processes via API.'''

    steps = SerializerMethodField(method_name='get_steps', read_only=True)      # Step details for read operations
    creator = SimplyUserSerializer(many=False, read_only=True)                  # Creator details for read operations
    tags = RekonoTagField()                                                     # Tags

    class Meta:
        '''Serializer metadata.'''

        model = Process
        # Process fields exposed via API
        fields = ('id', 'name', 'description', 'creator', 'liked', 'likes', 'steps', 'tags')

    @extend_schema_field(StepSerializer(many=True, read_only=True))
    def get_steps(self, instance: Process) -> List[StepSerializer]:
        '''Get process steps sorted by configuration stage and priority (descendent).

        Args:
            instance (Process): Process instance

        Returns:
            List[StepSerializer]: Step list sorted by configuration stage and priority (descendent)
        '''
        return StepSerializer(instance.steps.all().order_by('configuration__stage', '-priority'), many=True).data


class SimplyProcessSerializer(serializers.ModelSerializer):
    '''Simply serializer to include process main data in other serializers.'''

    class Meta:
        '''Serializer metadata.'''

        model = Process
        fields = ('id', 'name')                                                 # Process fields exposed
