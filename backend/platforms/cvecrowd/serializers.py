"""Serializer of the CVE Crowd endpoints."""

from rest_framework.serializers import ModelSerializer

from framework.fields import ProtectedSecretField
from platforms.cvecrowd.integrations import CveCrowd
from platforms.cvecrowd.models import CveCrowdSettings


class CveCrowdSettingsSerializer(ModelSerializer):
    """Serializer of the CVE Crowd configuration.

    Attributes:
        api_token: API token, which is masked when the settings are read.
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")

    class Meta:
        """Serializer configuration for the CVE Crowd settings."""

        model = CveCrowdSettings
        fields = ("id", "trending_span_days", "execute_per_execution", "api_token", "is_available")
        read_only_fields = ("is_available",)

    def update(self, instance, validated_data):
        """Update the configuration and check if the platform answers with it.

        Args:
            instance: Settings being updated.
            validated_data: New settings values, already validated.

        Returns:
            The updated settings, which is where the result of the check is
            stored, since it isn't repeated until the token changes again.
        """
        instance = super().update(instance, validated_data)
        instance.is_available = CveCrowd().live_is_available()
        instance.save(update_fields=["is_available"])
        return instance
