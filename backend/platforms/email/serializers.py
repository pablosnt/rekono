"""Serializer of the SMTP endpoints."""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.email.models import SMTPSettings
from platforms.email.notifications import SMTP


class SMTPSettingsSerializer(ModelSerializer):
    """Serializer of the SMTP configuration.

    Attributes:
        password: Password, which is masked when the settings are read.
        is_available: Whether the configured server accepts a connection.
    """

    password = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        """Serializer configuration for the SMTP settings."""

        model = SMTPSettings
        fields = ("id", "host", "port", "username", "password", "tls", "is_available")

    def get_is_available(self, instance: SMTPSettings) -> bool:
        """Check if the configured server accepts a connection.

        Args:
            instance: Settings being serialized, not read because the check is
              performed against the live platform.

        Returns:
            Whether the platform answers with the configured settings.
        """
        return SMTP().is_available()
