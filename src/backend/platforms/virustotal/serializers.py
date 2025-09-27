"""Django REST Framework serializers for VirusTotal platform configuration.

This module provides serialization classes for VirusTotal platform settings
and configuration management through REST API endpoints. Supports secure
handling of API credentials and real-time platform availability checking.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

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
        is_available (SerializerMethodField): Real-time platform availability
                                              status
        client (VirusTotal): Integration client for availability checking
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)
    client = VirusTotal()

    class Meta:
        """Serializer metadata configuration.

        Defines the model and fields for VirusTotal settings serialization.
        Includes platform configuration ID, encrypted API token, and real-time
        availability status for comprehensive platform management.
        """

        model = VirusTotalSettings
        fields = ("id", "api_token", "is_available")

    def get_is_available(self, instance: VirusTotalSettings) -> bool:
        """Get real-time availability status of the VirusTotal platform.

        Checks if the VirusTotal platform is currently accessible and
        responsive
        by performing a test API request with the configured credentials.

        Args:
            instance (VirusTotalSettings): The settings instance being
                                          serialized

        Returns:
            bool: True if VirusTotal is available and accessible, False
                  otherwise
        """
        return self.client.is_available()
