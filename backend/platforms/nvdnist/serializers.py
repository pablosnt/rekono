"""Serializer of the NVD NIST endpoints."""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.nvdnist.integrations import NvdNist
from platforms.nvdnist.models import NvdNistSettings


class NvdNistSettingsSerializer(ModelSerializer):
    """Serializer of the NVD NIST configuration.

    Attributes:
        api_token: API token, which is masked when the settings are read.
        is_available: Whether the platform answers with the configured token.
        client: Client used to check if the platform answers.
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)
    client = NvdNist()

    class Meta:
        """Serializer configuration for the NVD NIST settings."""

        model = NvdNistSettings
        fields = ("id", "api_token", "is_available")

    def get_is_available(self, instance: NvdNistSettings) -> bool:
        """Check if the platform can be used with the configured token.

        Args:
            instance: Settings being serialized, not read because the check is
              performed against the live platform.

        Returns:
            Whether the platform answers with the configured settings.
        """
        return self.client.is_available()
