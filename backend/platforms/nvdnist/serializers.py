"""Django REST framework serializers for NVD NIST platform management.

Serializer classes for converting NVD NIST settings models to/from JSON
for API operations. Includes validation logic and computed availability status.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.nvdnist.integrations import NvdNist
from platforms.nvdnist.models import NvdNistSettings


class NvdNistSettingsSerializer(ModelSerializer):
    """Serializer for NVD NIST platform settings.

    Handles serialization and deserialization of NvdNistSettings objects
    for API operations. Includes protected secret field handling and
    computed availability status based on API token validation.

    Attributes:
        api_token (ProtectedSecretField): Secured API token field with validation
        is_available (SerializerMethodField): Computed field for API availability status
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)
    client = NvdNist()

    class Meta:
        """Meta configuration for NvdNistSettingsSerializer.

        Attributes:
            model (Model): The NvdNistSettings model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = NvdNistSettings
        fields = ("id", "api_token", "is_available")

    def get_is_available(self, instance: NvdNistSettings) -> bool:
        """Check if NVD NIST API integration is available and functional.

        Validates the configured API token by testing connectivity to the
        NVD NIST API service and returns availability status.

        Args:
            instance (NvdNistSettings): The settings instance being serialized

        Returns:
            bool: True if API integration is available and working, False otherwise
        """
        return self.client.is_api_token_available
