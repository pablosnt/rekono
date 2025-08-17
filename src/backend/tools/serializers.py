from typing import Any

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import IntegerChoicesField
from framework.serializers import LikeSerializer
from input_types.enums import InputTypeName
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage
from tools.fields import StageField
from tools.models import Argument, Configuration, Intensity, Tool


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
    input_technologies = SerializerMethodField(read_only=True)
    input_vulnerabilities = SerializerMethodField(read_only=True)

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
            "input_technologies",
            "input_vulnerabilities",
        )

    def _get_argument_requirement(self, tool: Tool, input_type: InputTypeName) -> dict[str, bool]:
        argument = Argument.objects.filter(tool=tool, inputs__type__name=input_type)
        return (
            {"required": argument.first().required, "supported": True}
            if argument.exists()
            else {"required": False, "supported": False}
        )

    def get_wordlists(self, instance: Any) -> dict[str, bool]:
        output = self._get_argument_requirement(instance, InputTypeName.WORDLIST)
        if instance.name == "Gobuster":
            # There are two wordlist arguments for Gobuster, one to get a
            # subdomains wordlist and other to get an endpoints wordlist.
            # So, none can be marked as required, but they actually are
            output["required"] = True
        return output

    def get_input_technologies(self, instance: Any) -> dict[str, bool]:
        return self._get_argument_requirement(instance, InputTypeName.TECHNOLOGY)

    def get_input_vulnerabilities(self, instance: Any) -> dict[str, bool]:
        return self._get_argument_requirement(instance, InputTypeName.VULNERABILITY)


class SimpleToolSerializer(ModelSerializer):
    class Meta:
        model = Tool
        fields = ("id", "name", "command", "version", "reference", "icon")


class ConfigurationSerializer(SimpleConfigurationSerializer):
    tool = SimpleToolSerializer(many=False, read_only=True)

    class Meta:
        model = Configuration
        fields = SimpleConfigurationSerializer.Meta.fields + ("tool",)
