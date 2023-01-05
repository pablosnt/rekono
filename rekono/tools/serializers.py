from typing import List

from api.fields import IntegerChoicesField
from drf_spectacular.utils import extend_schema_field
from input_types.serializers import InputTypeSerializer
from likes.serializers import LikeBaseSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from tools.enums import IntensityRank, Stage
from tools.models import (Argument, Configuration, Input, Intensity, Output,
                          Tool)


class StageField(IntegerChoicesField):
    '''Serializer field to manage Stage values.'''

    model = Stage

    def to_representation(self, value: int) -> str:
        '''Return text value to send to the client.

        Args:
            value (int): Integer value of the IntegerChoices field

        Returns:
            str: String value associated to the integer
        '''
        if value == 1:                                                          # OSINT stage
            return super().to_representation(value).upper()
        return super().to_representation(value)


class IntensityField(IntegerChoicesField):
    '''Serializer field to manage Intensity values.'''

    model = IntensityRank


class InputSerializer(serializers.ModelSerializer):
    '''Serializer to get Input data via API.'''

    type = InputTypeSerializer(many=False, read_only=True)                      # Input type deatils for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Input
        fields = ('type', 'filter', 'order')                                    # Input fields exposed via API


class OutputSerializer(serializers.ModelSerializer):
    '''Serializer to get Output data via API.'''

    type = InputTypeSerializer(many=False, read_only=True)                      # Input type deatils for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Output
        fields = ('type',)                                                      # Output fields exposed via API


class ConfigurationSerializer(serializers.ModelSerializer):
    '''Serializer to get Configuration data via API.'''

    stage_name = StageField(source='stage')                                     # Stage name for read operations
    outputs = SerializerMethodField(method_name='get_outputs', read_only=True)  # Outputs details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Configuration
        # Configuration fields exposed via API
        fields = ('id', 'name', 'tool', 'arguments', 'stage_name', 'default', 'outputs')

    def get_outputs(self, instance: Configuration) -> OutputSerializer:
        '''Get configuration outputs sorted by Id.

        Args:
            instance (Configuration): Configuration instance

        Returns:
            OutputSerializer: Output list sorted by Id
        '''
        return OutputSerializer(instance.outputs.all().order_by('id'), many=True).data


class IntensitySerializer(serializers.ModelSerializer):
    '''Serializer to get Intensity data vai API.'''

    intensity_rank = IntensityField(source='value')                             # Intensity name for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Intensity
        fields = ('argument', 'intensity_rank')                                 # Intensity fields exposed via API


class ArgumentSerializer(serializers.ModelSerializer):
    '''Serializer to get Argument data via API.'''

    inputs = SerializerMethodField(method_name='get_inputs', read_only=True)    # Inputs details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Argument
        fields = ('name', 'argument', 'required', 'multiple', 'inputs')         # Argument fields exposed via API

    def get_inputs(self, instance: Argument) -> InputSerializer:
        '''Get argument inputs sorted by preference order.

        Args:
            instance (Argument): Argument instance

        Returns:
            InputSerializer: Input list sorted by order
        '''
        return InputSerializer(instance.inputs.all().order_by('order'), many=True).data


class ToolSerializer(serializers.ModelSerializer, LikeBaseSerializer):
    '''Serializer to get Tool data via API.'''

    # Intensitys details for read operations
    intensities = SerializerMethodField(method_name='get_intensities', read_only=True)
    # Configurations details for read operations
    configurations = SerializerMethodField(method_name='get_configurations', read_only=True)
    arguments = ArgumentSerializer(many=True, read_only=True)                   # Argument sdetails for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Tool
        fields = (                                                              # Tool fields exposed via API
            'id', 'name', 'command', 'reference', 'icon',
            'liked', 'likes', 'intensities', 'configurations', 'arguments'
        )

    @extend_schema_field(IntensitySerializer(many=True, read_only=True))
    def get_intensities(self, instance: Tool) -> List[IntensitySerializer]:
        '''Get tool intensities sorted by value (descendent).

        Args:
            instance (Tool): Tool instance

        Returns:
            InputSerializer: Intensity list sorted by value (descendent)
        '''
        return IntensitySerializer(instance.intensities.all().order_by('-value'), many=True).data

    @extend_schema_field(ConfigurationSerializer(many=True, read_only=True))
    def get_configurations(self, instance: Tool) -> List[ConfigurationSerializer]:
        '''Get tool configurations sorted by default (descendent) and name.

        Args:
            instance (Tool): Tool instance

        Returns:
            InputSerializer: Configuration list sorted by default (descendent) and name
        '''
        return ConfigurationSerializer(instance.configurations.all().order_by('-default', 'name'), many=True).data


class SimplyToolSerializer(serializers.ModelSerializer):
    '''Simply serializer to include tool main data in other serializers.'''

    arguments = ArgumentSerializer(many=True, read_only=True)                   # Arguments details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Tool
        # Tool fields exposed via API
        fields = ('id', 'name', 'command', 'reference', 'icon', 'arguments')
