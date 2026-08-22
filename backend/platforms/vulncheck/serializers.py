"""Serializer of the VulnCheck endpoints."""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.vulncheck.integrations import VulnCheck
from platforms.vulncheck.models import VulnCheckSettings


class VulnCheckSettingsSerializer(ModelSerializer):
    """Serializer of the VulnCheck configuration.

    Attributes:
        api_token: API token, which is masked when the settings are read.
        is_available: Whether the platform answers with the configured token.
        client: Client used to check if the platform answers.
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)
    client = VulnCheck()

    class Meta:
        """Serializer configuration for the VulnCheck settings."""

        model = VulnCheckSettings
        fields = ("id", "api_token", "is_available")

    def get_is_available(self, instance: VulnCheckSettings) -> bool:
        """Check if the platform can be used with the configured token.

        Args:
            instance: Settings being serialized, not read because the check is
              performed against the live platform.

        Returns:
            Whether the platform answers with the configured settings.
        """
        return self.client.is_available()
