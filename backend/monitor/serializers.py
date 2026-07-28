"""Django REST framework serializers for monitor settings management.

Serializer class for converting MonitorSettings model to/from JSON for API
operations. Provides read-only access to monitoring execution state while
allowing the monitoring interval to be updated.
"""

from rest_framework.serializers import ModelSerializer

from monitor.models import MonitorSettings


class MonitorSettingsSerializer(ModelSerializer):
    """Serializer for MonitorSettings model.

    Handles serialization and deserialization of MonitorSettings objects for
    API operations. Exposes the monitoring interval as a writable field while
    keeping the identifier and last execution timestamp read-only.
    """

    class Meta:
        """Meta configuration for the MonitorSettingsSerializer.

        Attributes:
            model (Model): The MonitorSettings model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified
        """

        model = MonitorSettings
        fields = ("id", "last_monitor", "hour_span")
        read_only_fields = ("id", "last_monitor")
