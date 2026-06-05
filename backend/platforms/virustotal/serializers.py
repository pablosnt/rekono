"""Django REST Framework serializers for VirusTotal platform configuration.

This module provides serialization classes for VirusTotal platform settings
and configuration management through REST API endpoints. Supports secure
handling of API credentials and real-time platform availability checking.
"""

from rest_framework.serializers import ModelSerializer

from framework.fields import ProtectedSecretField
from platforms.virustotal.integrations import VirusTotal
from platforms.virustotal.models import VirusTotalSettings


class VirusTotalSettingsSerializer(ModelSerializer):
    """Serializer for VirusTotal platform configuration settings.

    Provides secure serialization of VirusTotal platform settings including
    encrypted API token handling and real-time availability checking.
    Supports configuration management through REST API endpoints.

    Attributes:
        api_token (ProtectedSecretField): Secure API token field with
                                          encryption
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")

    class Meta:
        model = VirusTotalSettings
        fields = ("id", "api_token", "is_available")
        read_only_fields = ("is_available",)

    def update(self, instance, validated_data):
        """Update VirusTotal settings and refresh the platform availability status.

        Delegates to the parent update method, then performs a live API check to
        update the is_available field in the database.

        Args:
            instance (VirusTotalSettings): The settings instance to update.
            validated_data (dict): Validated data from the request.

        Returns:
            VirusTotalSettings: The updated settings instance.
        """
        instance = super().update(instance, validated_data)
        instance.is_available = VirusTotal().live_is_available()
        instance.save(update_fields=["is_available"])
        return instance
