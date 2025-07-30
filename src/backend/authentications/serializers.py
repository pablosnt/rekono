"""Django REST framework serializers for authentication models.

This module provides serialization and deserialization capabilities for
authentication records, including proper handling of sensitive data
with validation and protection.
"""

from rest_framework.serializers import ModelSerializer

from authentications.models import Authentication
from framework.fields import ProtectedSecretField
from security.validators.input_validator import Regex, Validator


class AuthenticationSerializer(ModelSerializer):
    """Serializer for Authentication model.

    This serializer handles the conversion of Authentication model instances
    to and from JSON format, with special handling for the secret field
    using ProtectedSecretField for enhanced security.

    Attributes:
        secret (ProtectedSecretField): Protected field for handling
            authentication secrets with validation.
    """

    secret = ProtectedSecretField(
        Validator(Regex.SECRET.value, code="secret").__call__,
        required=True,
        allow_null=False,
    )

    class Meta:
        """Meta configuration for the AuthenticationSerializer.

        Attributes:
            model: The Authentication model to serialize.
            fields: Tuple of field names to include in serialization.
        """

        model = Authentication
        fields = ("id", "name", "secret", "type", "target_port")
