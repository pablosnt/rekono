from tools.models import Intensity, Tool
from rest_framework import serializers
from tools.models import Configuration, Input, Output


class InputSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    selection = serializers.CharField(source='get_selection_display')

    class Meta:
        model = Input
        fields = ('name', 'type', 'argument', 'filter', 'selection', 'required')


class OutputSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = Output
        fields = ('type',)


class ConfigurationSerializer(serializers.ModelSerializer):
    inputs = InputSerializer(read_only=True, many=True, required=False)
    outputs = OutputSerializer(read_only=True, many=True, required=False)

    class Meta:
        model = Configuration
        fields = ('id', 'name', 'tool', 'arguments', 'default', 'inputs', 'outputs')


class IntensitySerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='get_value_display')

    class Meta:
        model = Intensity
        fields = ('argument', 'value')


class ToolSerializer(serializers.ModelSerializer):
    intensities = IntensitySerializer(read_only=True, many=True, required=False)
    configurations = ConfigurationSerializer(read_only=True, many=True, required=False)
    stage = serializers.CharField(source='get_stage_display')

    class Meta:
        model = Tool
        fields = ('id', 'name', 'command', 'stage', 'reference', 'intensities', 'configurations')
