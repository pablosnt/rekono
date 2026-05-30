"""Django REST framework serializers for VulnCheck platform management.

Serializer classes for converting VulnCheck settings models to/from JSON
for API operations. Includes validation logic and computed availability status.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.vulncheck.integrations import VulnCheck
from platforms.vulncheck.models import VulnCheckSettings


class VulnCheckSettingsSerializer(ModelSerializer):
    """Serializer for VulnCheck platform settings.

    Handles serialization and deserialization of VulnCheckSettings objects
    for API operations. Includes protected secret field handling and
    computed availability status based on Bearer token validation.

    Attributes:
        api_token (ProtectedSecretField): Secured Bearer token field with masking
        is_available (SerializerMethodField): Computed field for API availability status
        client (VulnCheck): Shared integration client instance for availability checks
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)
    client = VulnCheck()

    class Meta:
        """Meta configuration for VulnCheckSettingsSerializer.

        Attributes:
            model (Model): The VulnCheckSettings model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = VulnCheckSettings
        fields = ("id", "api_token", "is_available")

    def get_is_available(self, instance: VulnCheckSettings) -> bool:
        """Check if VulnCheck NVD++ API integration is available and functional.

        Validates the configured Bearer token by testing connectivity to the
        VulnCheck NVD++ API service and returns availability status.

        Args:
            instance (VulnCheckSettings): The settings instance being serialized.

        Returns:
            bool: True if API integration is available and working, False otherwise.
        """
        return self.client.is_available()
