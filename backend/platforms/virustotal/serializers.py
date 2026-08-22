"""Serializer of the VirusTotal endpoints."""

from rest_framework.serializers import ModelSerializer

from framework.fields import ProtectedSecretField
from platforms.virustotal.integrations import VirusTotal
from platforms.virustotal.models import VirusTotalSettings


class VirusTotalSettingsSerializer(ModelSerializer):
    """Serializer of the VirusTotal configuration.

    Attributes:
        api_token: API token, which is masked when the settings are read.
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")

    class Meta:
        """Serializer configuration for the VirusTotal settings."""

        model = VirusTotalSettings
        fields = ("id", "api_token", "is_available")
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
        instance.is_available = VirusTotal().live_is_available()
        instance.save(update_fields=["is_available"])
        return instance
