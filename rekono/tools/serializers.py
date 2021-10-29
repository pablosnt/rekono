from rest_framework import serializers
from tools.models import Configuration, Input, Intensity, Output, Tool


class InputSerializer(serializers.ModelSerializer):

    class Meta:
        model = Input
        fields = ('name', 'type', 'argument', 'filter', 'selection', 'required')
        ordering = ['-id']


class OutputSerializer(serializers.ModelSerializer):

    class Meta:
        model = Output
        fields = ('type',)
        ordering = ['-id']


class ConfigurationSerializer(serializers.ModelSerializer):
    inputs = InputSerializer(read_only=True, many=True, required=False)
    outputs = OutputSerializer(read_only=True, many=True, required=False)

    class Meta:
        model = Configuration
        fields = ('id', 'name', 'tool', 'arguments', 'default', 'inputs', 'outputs')
        ordering = ['-id']


class IntensitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Intensity
        fields = ('argument', 'value')
        ordering = ['-id']


class ToolSerializer(serializers.ModelSerializer):
    intensities = IntensitySerializer(read_only=True, many=True, required=False)
    configurations = ConfigurationSerializer(read_only=True, many=True, required=False)

    class Meta:
        model = Tool
        fields = (
            'id', 'name', 'command', 'stage', 'reference', 'icon',
            'for_each_target_port', 'intensities', 'configurations'
        )
        ordering = ['-id']
