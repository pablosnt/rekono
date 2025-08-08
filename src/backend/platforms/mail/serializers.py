"""Django REST framework serializers for SMTP settings management.

Provides serializer classes for SMTP configuration with secure handling of
sensitive credential data and service availability validation.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.mail.models import SMTPSettings
from platforms.mail.notifications import SMTP
from security.validators.input_validator import Regex, Validator


class SMTPSettingsSerializer(ModelSerializer):
    """Serializer for SMTP settings configuration with security validation.

    Provides secure serialization of SMTP server configuration including
    protected password field handling and service availability checking.
    Includes input validation and secure credential management.

    Attributes:
        password (ProtectedSecretField): Secure password field with validation
        is_available (SerializerMethodField): Real-time SMTP service availability status
    """

    password = ProtectedSecretField(
        Validator(Regex.SECRET, code="password").__call__, required=False, allow_null=True, source="secret"
    )
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        """Serializer metadata configuration for SMTPSettings model.

        Defines the model to serialize and specifies the fields to include
        in the serialized representation for REST API operations.

        Attributes:
            model: SMTPSettings model class for serialization
            fields: Tuple of field names to include in serialization
        """

        model = SMTPSettings
        fields = ("id", "host", "port", "username", "password", "tls", "is_available")

    def get_is_available(self, instance: SMTPSettings) -> bool:
        """Check if SMTP service is currently available and functional.

        Tests SMTP connection and configuration to determine if email
        notifications can be successfully delivered.

        Args:
            instance (SMTPSettings): SMTP settings instance to test

        Returns:
            bool: True if SMTP service is available and functional, False otherwise
        """
        return SMTP().is_available()
