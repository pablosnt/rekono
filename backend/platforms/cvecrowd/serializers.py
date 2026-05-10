"""Django REST framework serializers for CVE Crowd platform management.

Serializer classes for converting CVE Crowd settings models to/from JSON
for API operations. Includes secure credential handling, validation logic,
and platform availability detection for threat intelligence integration.
"""

from rest_framework.serializers import ModelSerializer

from framework.fields import ProtectedSecretField
from platforms.cvecrowd.integrations import CveCrowd
from platforms.cvecrowd.models import CveCrowdSettings


class CveCrowdSettingsSerializer(ModelSerializer):
    """Serializer for CVE Crowd platform settings.

    Handles serialization and deserialization of CVE Crowd settings with
    secure API token management and platform availability validation.
    Provides protected credential handling and real-time availability status.

    Attributes:
        api_token (ProtectedSecretField): Protected API token field with validation
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")

    class Meta:
        model = CveCrowdSettings
        fields = ("id", "trending_span_days", "execute_per_execution", "api_token", "is_available")
        read_only_fields = ("is_available",)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.is_available = len(CveCrowd().get_trending_cves(False)) > 0
        instance.save(update_fields=["is_available"])
        return instance
