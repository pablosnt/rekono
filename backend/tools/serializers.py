"""Serializers of the tool endpoints."""

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
    """Serializer of an intensity that a tool supports.

    Attributes:
        value: Intensity as its name instead of as the number that is stored.
    """

    value = IntegerChoicesField(model=IntensityEnum)

    class Meta:
        """Serializer configuration for the intensities."""

        model = Intensity
        fields = ("id", "argument", "value")


class SimpleConfigurationSerializer(ModelSerializer):
    """Serializer of a configuration to be included in other responses.

    Attributes:
        stage: Phase of the assessment as its name instead of as the number that
          is stored.
    """

    stage = StageField(model=Stage)

    class Meta:
        """Serializer configuration including only the configuration fields."""

        model = Configuration
        fields = ("id", "name", "stage", "default")


class ToolSerializer(LikeSerializer):
    """Serializer of a tool, including what it can do and how.

    Attributes:
        intensities: Intensities that the tool supports.
        configurations: Things that the tool can do, without the deprecated ones.
    """

    intensities = IntensitySerializer(many=True, read_only=True)
    configurations = SerializerMethodField(read_only=True)

    def get_configurations(self, instance: Tool) -> list[SimpleConfigurationSerializer]:
        """Get the configurations of the tool that can still be used.

        Args:
            instance: Tool being serialized.

        Returns:
            The serialized configurations, without the deprecated ones.
        """
        return SimpleConfigurationSerializer(instance.configurations.filter(deprecated=False), many=True).data

    class Meta:
        """Serializer configuration for the tools."""

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
        )


class SimpleToolSerializer(ModelSerializer):
    """Serializer of a tool to be included in other responses."""

    class Meta:
        """Serializer configuration including only the tool fields."""

        model = Tool
        fields = ("id", "name", "command", "version", "reference", "icon")


class ConfigurationSerializer(SimpleConfigurationSerializer):
    """Serializer of a configuration, including the data that it needs to run.

    The data that the users must provide is reported apart from the rest of the
    arguments, so the frontend knows which fields to ask for when a task with this
    configuration is created.

    Attributes:
        tool: Tool that the configuration belongs to.
        wordlists: Whether the configuration accepts wordlists, and whether it
          needs them to run.
        input_technologies: Whether the configuration accepts technologies provided
          by the users, and whether it needs them to run.
        input_vulnerabilities: Whether the configuration accepts vulnerabilities
          provided by the users, and whether it needs them to run.
    """

    tool = SimpleToolSerializer(many=False, read_only=True)
    wordlists = SerializerMethodField(read_only=True)
    input_technologies = SerializerMethodField(read_only=True)
    input_vulnerabilities = SerializerMethodField(read_only=True)

    class Meta:
        """Serializer configuration adding the tool data to the configuration one."""

        model = Configuration
        fields = SimpleConfigurationSerializer.Meta.fields + (
            "tool",
            "wordlists",
            "input_technologies",
            "input_vulnerabilities",
        )

    def _get_argument_requirement(self, configuration: Configuration, input_type: InputTypeName) -> dict[str, bool]:
        """Check if a configuration accepts an input type, and if it needs it.

        Args:
            configuration: Configuration whose arguments are inspected.
            input_type: Input type searched among those arguments.

        Returns:
            The ``supported`` and ``required`` flags that the frontend reads to
            decide which fields to ask for.
        """
        argument = Argument.objects.filter(configuration=configuration, inputs__type__name=input_type)
        return (
            {"required": argument.first().required, "supported": True}
            if argument.exists()
            else {"required": False, "supported": False}
        )

    def get_wordlists(self, instance: Any) -> dict[str, bool]:
        """Check if the configuration accepts wordlists, and if it needs them.

        Args:
            instance: Configuration being serialized.

        Returns:
            The ``supported`` and ``required`` flags for the wordlists.
        """
        return self._get_argument_requirement(instance, InputTypeName.WORDLIST)

    def get_input_technologies(self, instance: Any) -> dict[str, bool]:
        """Check if the configuration accepts technologies, and if it needs them.

        Args:
            instance: Configuration being serialized.

        Returns:
            The ``supported`` and ``required`` flags for the technologies.
        """
        return self._get_argument_requirement(instance, InputTypeName.TECHNOLOGY)

    def get_input_vulnerabilities(self, instance: Any) -> dict[str, bool]:
        """Check if the configuration accepts vulnerabilities, and if it needs them.

        Args:
            instance: Configuration being serialized.

        Returns:
            The ``supported`` and ``required`` flags for the vulnerabilities.
        """
        return self._get_argument_requirement(instance, InputTypeName.VULNERABILITY)
