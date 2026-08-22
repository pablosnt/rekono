"""Serializer of the monitor endpoints."""

from rest_framework.serializers import ModelSerializer

from monitor.models import MonitorSettings


class MonitorSettingsSerializer(ModelSerializer):
    """Serializer of the monitor configuration.

    Only the interval between runs can be changed, since the rest of the data is
    written by the monitor job itself.
    """

    class Meta:
        """Serializer configuration for the monitor settings."""

        model = MonitorSettings
        fields = ("id", "last_monitor", "hour_span")
        read_only_fields = ("id", "last_monitor")
