from framework.fields import IntegerChoicesField
from framework.serializers import LikeSerializer
from input_types.serializers import InputTypeSerializer
from rest_framework.serializers import ModelSerializer
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage
from tools.fields import StageField
from tools.models import Argument, Configuration, Input, Intensity, Output, Tool


class InputSerializer(ModelSerializer):
    type = InputTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Input
        fields = ("id", "type", "filter", "order")


class OutputSerializer(ModelSerializer):
    type = InputTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Output
        fields = (
            "id",
            "type",
        )


class IntensitySerializer(ModelSerializer):
    value = IntegerChoicesField(model=IntensityEnum)

    class Meta:
        model = Intensity
        fields = ("id", "argument", "value")


class ArgumentSerializer(ModelSerializer):
    inputs = InputSerializer(many=True)

    class Meta:
        model = Argument
        fields = (
            "id",
            "name",
            "argument",
            "required",
            "multiple",
            "inputs",
        )


class SimpleConfigurationSerializer(ModelSerializer):
    stage = StageField(model=Stage)
    outputs = OutputSerializer(many=True)

    class Meta:
        model = Configuration
        fields = ("id", "name", "tool", "arguments", "stage", "default", "outputs")


class ToolSerializer(LikeSerializer):
    intensities = IntensitySerializer(many=True)
    configurations = SimpleConfigurationSerializer(many=True)
    arguments = ArgumentSerializer(many=True)

    class Meta:
        model = Tool
        fields = (
            "id",
            "name",
            "command",
            "version",
            "reference",
            "icon",
            "liked",
            "likes",
            "intensities",
            "configurations",
            "arguments",
        )


class SimpleToolSerializer(ModelSerializer):
    class Meta:
        model = Tool
        fields = (
            "id",
            "name",
            "command",
            "version",
            "reference",
            "icon",
        )


class ConfigurationSerializer(SimpleConfigurationSerializer):
    tool = SimpleToolSerializer()
