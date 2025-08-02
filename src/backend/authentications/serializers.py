"""Django REST framework serializers for authentication models.

Provides serialization for authentication records with secure handling
of sensitive credential data using protected fields and validation.
"""

from rest_framework.serializers import ModelSerializer

from authentications.models import Authentication
from framework.fields import ProtectedSecretField
from security.validators.input_validator import Regex, Validator


class AuthenticationSerializer(ModelSerializer):
    """Serializer for Authentication model.

    Handles serialization of Authentication instances with secure handling
    of the secret field using ProtectedSecretField for enhanced security.

    Attributes:
        secret (ProtectedSecretField): Protected field for credential secrets
    """

    secret = ProtectedSecretField(
        Validator(Regex.SECRET.value, code="secret").__call__,
        required=True,
        allow_null=False,
    )

    class Meta:
        """Meta configuration for the AuthenticationSerializer.

        Attributes:
            model (Model): The Authentication model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = Authentication
        fields = ("id", "name", "secret", "type", "target_port")
