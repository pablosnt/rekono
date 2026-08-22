"""Serializers of the process and step endpoints."""

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
    """Serializer with the minimum data needed to reference a process."""

    class Meta:
        """Serializer configuration for the process references."""

        model = Process
        fields = ("id", "name")


class SimpleStepSerializer(ModelSerializer):
    """Serializer of a step, including the configuration that it executes.

    Attributes:
        configuration_id: Configuration to be executed, which can only be one of
          the configurations that aren't deprecated.
        configuration: Data of that configuration.
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
        """Serializer configuration for the steps of a known process."""

        model = Step
        fields = ("id", "process", "configuration_id", "configuration")


class StepSerializer(SimpleStepSerializer):
    """Serializer of a step, including the process that contains it.

    Attributes:
        process_id: Process that will contain the step.
        process: Data of that process.
    """

    process_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=True, source="process", queryset=Process.objects.all()
    )
    process = SimpleProcessSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration for the steps."""

        model = Step
        fields = SimpleStepSerializer.Meta.fields + ("process_id",)


class ProcessSerializer(TaggitSerializer, LikeSerializer):
    """Serializer of a process, including its steps and the likes of the users.

    Attributes:
        steps: Steps of the process that can still be executed.
        owner: User that created the process.
        tags: Labels assigned to the process.
        wordlists: Whether the process supports and requires wordlists.
    """

    steps = SerializerMethodField(read_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()
    wordlists = SerializerMethodField(read_only=True)

    class Meta:
        """Serializer configuration for the processes."""

        model = Process
        fields = ("id", "name", "description", "owner", "liked", "likes", "steps", "tags", "wordlists")

    def get_steps(self, instance: Process) -> list[SimpleStepSerializer]:
        """Get the steps of the process whose configuration isn't deprecated.

        Deprecated configurations are kept in the database to preserve historical
        data consistency, but they must not be exposed as selectable process steps.

        Args:
            instance: Process being serialized.

        Returns:
            The serialized steps that can still be executed.
        """
        return SimpleStepSerializer(instance.steps.filter(configuration__deprecated=False), many=True).data

    def get_wordlists(self, instance: Any) -> dict[str, bool]:
        """Check how the process uses the wordlists.

        Args:
            instance: Process being serialized.

        Returns:
            Whether any step requires a wordlist, so the process can't be executed
            without one, and whether any step supports it, so the users know if
            selecting one changes anything.
        """
        return {
            "required": Argument.objects.filter(
                inputs__type__name=InputTypeName.WORDLIST.value, required=True, configuration__steps__process=instance
            ).exists(),
            "supported": instance.steps.filter(
                configuration__arguments__inputs__type__name=InputTypeName.WORDLIST.value
            ).exists(),
        }
