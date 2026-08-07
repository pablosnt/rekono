"""Serializers of the target denylist endpoints."""

from rest_framework.serializers import ModelSerializer

from target_denylist.models import TargetDenylist


class TargetDenylistSerializer(ModelSerializer):
    """Serializer of a denylist entry.

    The default and blocked fields are read-only: default marks the entries
    provided by Rekono, and blocked is a counter maintained by the target validator.
    """

    class Meta:
        """Serializer configuration for the denylist entries."""

        model = TargetDenylist
        fields = ("id", "target", "default", "blocked")
        read_only_fields = ("default", "blocked")
