from rest_framework.serializers import ModelSerializer
from target_blacklist.models import TargetBlacklist


class TargetBlacklistSerializer(ModelSerializer):
    class Meta:
        model = TargetBlacklist
        fields = ("id", "target", "default")
        read_only_fields = ("default",)
