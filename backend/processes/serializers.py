"""Django REST framework serializers for process management operations.

Serializer classes for converting process and step models to/from JSON
for API operations. Includes validation logic, computed fields, and
nested serialization for complex process workflow management.
"""

from typing import Any

from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)
from taggit.serializers import TaggitSerializer

from framework.fields import TagField
from framework.serializers import LikeSerializer
from input_types.enums import InputTypeName
from processes.models import Process, Step
from tools.models import Argument, Configuration
from tools.serializers import ConfigurationSerializer
from users.serializers import SimpleUserSerializer


class SimpleProcessSerializer(ModelSerializer):
    """Serializer for simplified Process representation.

    Provides basic process information for nested serialization and
    reference purposes without detailed process data.
    """

    class Meta:
        """Meta configuration for SimpleProcessSerializer.

        Defines the model and fields for basic process serialization used
        in nested representations and reference purposes.

        Attributes:
            model (Model): The Process model to serialize
            fields (tuple): Basic fields for simplified process representation
        """

        model = Process
        fields = ("id", "name")


class SimpleStepSerializer(ModelSerializer):
    """Serializer for Step model with configuration details.

    Handles serialization of process steps with nested configuration
    information and primary key relationships for API operations.

    Attributes:
        configuration_id (PrimaryKeyRelatedField): Write-only configuration reference
        configuration (ConfigurationSerializer): Read-only configuration details
    """

    configuration_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=True,
        source="configuration",
        queryset=Configuration.objects.filter(deprecated=False),
    )
    configuration = ConfigurationSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for SimpleStepSerializer.

        Defines the model and fields for step serialization with configuration
        details and primary key relationships.

        Attributes:
            model (Model): The Step model to serialize
            fields (tuple): Fields including step identifiers, process reference,
                           and configuration details
        """

        model = Step
        fields = ("id", "process", "configuration_id", "configuration")


class StepSerializer(SimpleStepSerializer):
    """Extended serializer for Step model with process relationships.

    Extends SimpleStepSerializer with process reference handling for
    complete step management including both process and configuration details.

    Attributes:
        process_id (PrimaryKeyRelatedField): Write-only process reference
        process (SimpleProcessSerializer): Read-only process details
    """

    process_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=True, source="process", queryset=Process.objects.all()
    )
    process = SimpleProcessSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for StepSerializer.

        Extends SimpleStepSerializer's Meta configuration with additional
        process reference field for complete step management.

        Attributes:
            model (Model): The Step model to serialize
            fields (tuple): Extended fields including all SimpleStepSerializer fields
                           plus process_id for write operations
        """

        model = Step
        fields = SimpleStepSerializer.Meta.fields + ("process_id",)


class ProcessSerializer(TaggitSerializer, LikeSerializer):
    """Comprehensive serializer for Process model with community features.

    Handles serialization and deserialization of Process objects with complete
    workflow information including steps, tags, user interactions, and
    wordlist compatibility detection.

    Attributes:
        steps (SerializerMethodField): Non-deprecated step information (read-only)
        owner (SimpleUserSerializer): Process owner details (read-only)
        tags (TagField): Tag management field for categorization
        wordlists (SerializerMethodField): Wordlist compatibility information
    """

    steps = SerializerMethodField(read_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()
    wordlists = SerializerMethodField(read_only=True)

    class Meta:
        """Meta configuration for ProcessSerializer.

        Defines the model and comprehensive field set for complete process
        serialization including community features, workflow details, and
        computed information fields.

        Attributes:
            model (Model): The Process model to serialize
            fields (tuple): Complete field set including basic information,
                           community features, workflow steps, tags, and
                           computed wordlist compatibility data
        """

        model = Process
        fields = ("id", "name", "description", "owner", "liked", "likes", "steps", "tags", "wordlists")

    def get_steps(self, instance: Process) -> list[SimpleStepSerializer]:
        """Serialize the process steps whose configuration is not deprecated.

        Deprecated configurations are kept in the database to preserve historical
        data consistency, but they must not be exposed as selectable process steps.

        Args:
            instance (Process): The Process instance being serialized.

        Returns:
            list[SimpleStepSerializer]: Serialized steps backed by non-deprecated configurations.
        """
        return SimpleStepSerializer(instance.steps.filter(configuration__deprecated=False), many=True).data

    def get_wordlists(self, instance: Any) -> dict[str, bool]:
        """Determine wordlist compatibility for the process.

        Analyzes process steps to determine if wordlists are required or
        supported by any tools in the workflow, enabling proper resource
        preparation for process execution.

        Args:
            instance (Process): The Process instance being serialized.

        Returns:
            dict[str, bool]: Dictionary containing:
                - required: True if any step requires wordlists
                - supported: True if any step supports wordlists
        """
        return {
            "required": Argument.objects.filter(
                inputs__type__name=InputTypeName.WORDLIST.value, required=True, configuration__steps__process=instance
            ).exists(),
            "supported": instance.steps.filter(
                configuration__arguments__inputs__type__name=InputTypeName.WORDLIST.value
            ).exists(),
        }
