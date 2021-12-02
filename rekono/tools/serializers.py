from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
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
    inputs = SerializerMethodField(
        method_name='get_inputs',
        read_only=True,
        required=False
    )
    outputs = SerializerMethodField(
        method_name='get_outputs',
        read_only=True,
        required=False
    )

    class Meta:
        model = Configuration
        fields = ('id', 'name', 'tool', 'arguments', 'default', 'inputs', 'outputs')
        ordering = ['-id']

    def get_inputs(self, instance):
        return InputSerializer(instance.inputs.all().order_by('id'), many=True).data

    def get_outputs(self, instance):
        return OutputSerializer(instance.outputs.all().order_by('id'), many=True).data


class IntensitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Intensity
        fields = ('argument', 'value')
        ordering = ['-id']


class ToolSerializer(serializers.ModelSerializer):
    intensities = SerializerMethodField(
        method_name='get_intensities',
        read_only=True,
        required=False
    )
    configurations = SerializerMethodField(
        method_name='get_configurations',
        read_only=True,
        required=False
    )

    class Meta:
        model = Tool
        fields = (
            'id', 'name', 'command', 'stage', 'reference', 'icon',
            'for_each_target_port', 'intensities', 'configurations'
        )

    def get_intensities(self, instance):
        return IntensitySerializer(instance.intensities.all().order_by('value'), many=True).data

    def get_configurations(self, instance):
        return ConfigurationSerializer(
            instance.configurations.all().order_by('-default', 'name'),
            many=True
        ).data
