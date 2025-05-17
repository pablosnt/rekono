from typing import Any

from framework.fields import IntegerChoicesField
from framework.serializers import LikeSerializer
from input_types.enums import InputTypeName
from input_types.serializers import InputTypeSerializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage
from tools.fields import StageField
from tools.models import Argument, Configuration, Intensity, Output, Tool


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


class SimpleConfigurationSerializer(ModelSerializer):
    stage = StageField(model=Stage)

    class Meta:
        model = Configuration
        fields = ("id", "name", "stage", "default")


class ToolSerializer(LikeSerializer):
    intensities = IntensitySerializer(many=True, read_only=True)
    configurations = SimpleConfigurationSerializer(many=True, read_only=True)
    wordlists = SerializerMethodField(read_only=True)
    require_input_technology = SerializerMethodField(read_only=True)
    require_input_vulnerability = SerializerMethodField(read_only=True)

    class Meta:
        model = Tool
        fields = (
            "id",
            "name",
            "command",
            "script",
            "is_installed",
            "version",
            "reference",
            "icon",
            "liked",
            "likes",
            "intensities",
            "configurations",
            "wordlists",
            "require_input_technology",
            "require_input_vulnerability",
        )

    def get_wordlists(self, instance: Any) -> dict[str, bool]:
        queryset = Argument.objects.filter(tool=instance, inputs__type__name=InputTypeName.WORDLIST)
        return {
            "required": queryset.filter(required=True).exists() or instance.name == "Gobuster",
            "supported": queryset.exists(),
        }

    def get_require_input_technology(self, instance: Any) -> bool:
        return Argument.objects.filter(
            tool=instance, inputs__type__name=InputTypeName.TECHNOLOGY, required=True
        ).exists()

    def get_require_input_vulnerability(self, instance: Any) -> bool:
        return Argument.objects.filter(
            tool=instance, inputs__type__name=InputTypeName.VULNERABILITY, required=True
        ).exists()


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
    tool = SimpleToolSerializer(many=False, read_only=True)

    class Meta:
        model = Configuration
        fields = SimpleConfigurationSerializer.Meta.fields + ("tool",)
