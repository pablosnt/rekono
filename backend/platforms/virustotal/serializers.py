"""Django REST Framework serializers for VirusTotal platform configuration.

This module provides serialization classes for VirusTotal platform settings
and configuration management through REST API endpoints. Supports protected
handling of API credentials and refreshes the platform availability flag on update.
"""

from rest_framework.serializers import ModelSerializer

from framework.fields import ProtectedSecretField
from platforms.virustotal.integrations import VirusTotal
from platforms.virustotal.models import VirusTotalSettings


class VirusTotalSettingsSerializer(ModelSerializer):
    """Serializer for VirusTotal platform settings.

    Handles serialization and deserialization of VirusTotalSettings objects. Includes
    protected API token handling and refreshes the persisted availability flag whenever
    settings are updated through the API.

    Attributes:
        api_token (ProtectedSecretField): Secured API token field with masking
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")

    class Meta:
        """Meta configuration for VirusTotalSettingsSerializer.

        Attributes:
            model (Model): The VirusTotalSettings model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified via API
        """

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
