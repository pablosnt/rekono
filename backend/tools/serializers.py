"""Django REST framework serializers for tools and configurations.

Provides serializer classes for tools, configurations, and intensities with
complex computed fields, input type mappings, and nested relationship handling
for comprehensive tool information in API responses.
"""

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
    """Serializer for Intensity model with enum field handling.

    Handles serialization of intensity configurations with proper enum
    conversion for intensity values.

    Attributes:
        value (IntegerChoicesField): Intensity level with enum conversion
    """

    value = IntegerChoicesField(model=IntensityEnum)

    class Meta:
        """Meta configuration for the IntensitySerializer.

        Attributes:
            model (type): The Intensity model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = Intensity
        fields = ("id", "argument", "value")


class SimpleConfigurationSerializer(ModelSerializer):
    """Simplified serializer for Configuration model with stage enum handling.

    Provides basic configuration information with proper stage enum conversion.
    Used for nested relationships and list views.

    Attributes:
        stage (StageField): Execution stage with enum conversion
    """

    stage = StageField(model=Stage)

    class Meta:
        """Meta configuration for the SimpleConfigurationSerializer.

        Attributes:
            model (type): The Configuration model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = Configuration
        fields = ("id", "name", "stage", "default", "deprecated")


class ToolSerializer(LikeSerializer):
    """Comprehensive serializer for Tool model with nested relationships and computed fields.

    Provides complete tool information including intensities, configurations,
    and input requirement analysis for wordlists, technologies, and vulnerabilities.
    Extends LikeSerializer to include like functionality.

    Attributes:
        intensities (IntensitySerializer): Nested intensity configurations
        configurations (SimpleConfigurationSerializer): Nested tool configurations
    """

    intensities = IntensitySerializer(many=True, read_only=True)
    configurations = SimpleConfigurationSerializer(many=True, read_only=True)

    class Meta:
        """Meta configuration for the ToolSerializer.

        Attributes:
            model (type): The Tool model to serialize
            fields (tuple): Field names to include in serialization
        """

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
    """Simplified serializer for Tool model with basic information only.

    Provides essential tool information for nested relationships and
    list views where full detail is not required.
    """

    class Meta:
        """Meta configuration for the SimpleToolSerializer.

        Attributes:
            model (type): The Tool model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = Tool
        fields = ("id", "name", "command", "version", "reference", "icon")


class ConfigurationSerializer(SimpleConfigurationSerializer):
    """Extended serializer for Configuration model with nested tool information.

    Extends SimpleConfigurationSerializer to include nested tool details
    and computed requirement information for complete configuration data in API responses.

    Attributes:
        tool (SimpleToolSerializer): Nested tool information
        wordlists (SerializerMethodField): Wordlist requirement and support information
        input_technologies (SerializerMethodField): Technology input requirement analysis
        input_vulnerabilities (SerializerMethodField): Vulnerability input requirement analysis
    """

    tool = SimpleToolSerializer(many=False, read_only=True)
    wordlists = SerializerMethodField(read_only=True)
    input_technologies = SerializerMethodField(read_only=True)
    input_vulnerabilities = SerializerMethodField(read_only=True)

    class Meta:
        """Meta configuration for the ConfigurationSerializer.

        Attributes:
            model (type): The Configuration model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = Configuration
        fields = SimpleConfigurationSerializer.Meta.fields + (
            "tool",
            "wordlists",
            "input_technologies",
            "input_vulnerabilities",
        )

    def _get_argument_requirement(self, configuration: Configuration, input_type: InputTypeName) -> dict[str, bool]:
        """Get argument requirement information for a specific input type.

        Analyzes tool configurations and their arguments to determine if a specific input type is supported
        and whether it's required for tool execution.

        Args:
            configuration (Configuration): The tool instance to analyze
            input_type (InputTypeName): The input type to check requirements for

        Returns:
            dict[str, bool]: Dictionary with 'required' and 'supported' boolean flags
        """
        argument = Argument.objects.filter(configuration=configuration, inputs__type__name=input_type)
        return (
            {"required": argument.first().required, "supported": True}
            if argument.exists()
            else {"required": False, "supported": False}
        )

    def get_wordlists(self, instance: Any) -> dict[str, bool]:
        """Get wordlist requirement information for the tool.

        Args:
            instance (Tool): The tool instance being serialized

        Returns:
            dict[str, bool]: Dictionary with 'required' and 'supported' boolean flags
        """
        return self._get_argument_requirement(instance, InputTypeName.WORDLIST)

    def get_input_technologies(self, instance: Any) -> dict[str, bool]:
        """Get technology input requirement information for the tool.

        Args:
            instance (Tool): The tool instance being serialized

        Returns:
            dict[str, bool]: Dictionary with 'required' and 'supported' boolean flags
        """
        return self._get_argument_requirement(instance, InputTypeName.TECHNOLOGY)

    def get_input_vulnerabilities(self, instance: Any) -> dict[str, bool]:
        """Get vulnerability input requirement information for the tool.

        Args:
            instance (Tool): The tool instance being serialized

        Returns:
            dict[str, bool]: Dictionary with 'required' and 'supported' boolean flags
        """
        return self._get_argument_requirement(instance, InputTypeName.VULNERABILITY)
