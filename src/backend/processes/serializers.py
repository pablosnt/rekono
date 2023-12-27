from framework.fields import TagField
from framework.serializers import LikeSerializer
from processes.models import Process, Step
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from taggit.serializers import TaggitSerializer
from tools.models import Configuration
from tools.serializers import ConfigurationSerializer
from users.serializers import SimpleUserSerializer


class SimpleProcessSerializer(ModelSerializer):
    class Meta:
        model = Process
        fields = ("id", "name")


class SimpleStepSerializer(ModelSerializer):
    configuration_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=True,
        source="configuration",
        queryset=Configuration.objects.all(),
    )
    configuration = ConfigurationSerializer(many=False, read_only=True)

    class Meta:
        model = Step
        fields = (
            "id",
            "process",
            "configuration_id",
            "configuration",
        )


class StepSerializer(SimpleStepSerializer):
    process_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=True,
        source="process",
        queryset=Process.objects.all(),
    )
    process = SimpleProcessSerializer(many=False, read_only=True)

    class Meta:
        model = Step
        fields = SimpleStepSerializer.Meta.fields + ("process_id",)


class ProcessSerializer(TaggitSerializer, LikeSerializer):
    steps = SimpleStepSerializer(read_only=True, many=True)
    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()

    class Meta:
        model = Process
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "liked",
            "likes",
            "steps",
            "tags",
        )
