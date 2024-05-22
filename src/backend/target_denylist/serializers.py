from rest_framework.serializers import ModelSerializer
from target_denylist.models import TargetDenylist


class TargetDenylistSerializer(ModelSerializer):
    class Meta:
        model = TargetDenylist
        fields = ("id", "target", "default")
        read_only_fields = ("default",)
