from typing import List

from api.serializers import IntegerChoicesField
from drf_spectacular.utils import extend_schema_field
from input_types.serializers import InputTypeSerializer
from likes.serializers import LikeBaseSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from tools.enums import IntensityRank, Stage
from tools.models import (Argument, Configuration, Input, Intensity, Output,
                          Tool)


class StageField(IntegerChoicesField):
    model = Stage

    def to_representation(self, value) -> str:
        if value == 1:
            return super().to_representation(value).upper()
        return super().to_representation(value)


class IntensityField(IntegerChoicesField):
    model = IntensityRank


class InputSerializer(serializers.ModelSerializer):
    type = InputTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Input
        fields = ('type', 'filter', 'order')


class OutputSerializer(serializers.ModelSerializer):
    type = InputTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Output
        fields = ('type',)
        ordering = ['-id']


class ConfigurationSerializer(serializers.ModelSerializer):
    outputs = SerializerMethodField(method_name='get_outputs', read_only=True)

    class Meta:
        model = Configuration
        fields = ('id', 'name', 'tool', 'arguments', 'default', 'outputs')
        ordering = ['-id']

    def get_outputs(self, instance) -> OutputSerializer:
        return OutputSerializer(instance.outputs.all().order_by('id'), many=True).data


class IntensitySerializer(serializers.ModelSerializer):
    intensity_rank = IntensityField(source='value')

    class Meta:
        model = Intensity
        fields = ('argument', 'intensity_rank')
        ordering = ['-id']


class ArgumentSerializer(serializers.ModelSerializer):
    inputs = SerializerMethodField(method_name='get_inputs', read_only=True)

    class Meta:
        model = Argument
        fields = ('name', 'argument', 'required', 'multiple', 'inputs')
        ordering = ['-id']
    
    def get_inputs(self, instance) -> InputSerializer:
        return InputSerializer(instance.inputs.all().order_by('order'), many=True).data


class ToolSerializer(serializers.ModelSerializer, LikeBaseSerializer):
    stage_name = StageField(source='stage')
    intensities = SerializerMethodField(method_name='get_intensities', read_only=True)
    configurations = SerializerMethodField(method_name='get_configurations', read_only=True)
    arguments = ArgumentSerializer(many=True, read_only=True)

    class Meta:
        model = Tool
        fields = (
            'id', 'name', 'command', 'stage_name', 'reference', 'icon',
            'liked', 'likes', 'intensities', 'configurations', 'arguments'
        )

    @extend_schema_field(IntensitySerializer(many=True, read_only=True))
    def get_intensities(self, instance) -> List[IntensitySerializer]:
        return IntensitySerializer(instance.intensities.all().order_by('-value'), many=True).data

    @extend_schema_field(ConfigurationSerializer(many=True, read_only=True))
    def get_configurations(self, instance) -> List[ConfigurationSerializer]:
        return ConfigurationSerializer(
            instance.configurations.all().order_by('-default', 'name'),
            many=True
        ).data


class SimplyToolSerializer(serializers.ModelSerializer):
    stage_name = StageField(source='stage')
    arguments = ArgumentSerializer(many=True, read_only=True)

    class Meta:
        model = Tool
        fields = ('id', 'name', 'command', 'stage_name', 'reference', 'icon', 'arguments')
