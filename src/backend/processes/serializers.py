from framework.fields import TagField
from framework.serializers import LikeSerializer
from processes.models import Process, Step
from rest_framework.serializers import ModelSerializer
from taggit.serializers import TaggitSerializer
from tools.serializers import ConfigurationSerializer
from users.serializers import SimpleUserSerializer


class SimpleProcessSerializer(ModelSerializer):
    class Meta:
        model = Process
        fields = ("id", "name")


class SimpleStepSerializer(ModelSerializer):
    configuration = ConfigurationSerializer(many=False)

    class Meta:
        model = Step
        fields = (
            "id",
            "process",
            "configuration",
        )


class StepSerializer(SimpleStepSerializer):
    process = SimpleProcessSerializer(many=False)


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
