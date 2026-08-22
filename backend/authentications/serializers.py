"""Serializers of the authentication endpoints."""

from rest_framework.serializers import ModelSerializer

from authentications.models import Authentication
from framework.fields import ProtectedSecretField


class AuthenticationSerializer(ModelSerializer):
    """Serializer of a credential, whose secret is masked when it's read.

    Attributes:
        secret: Secret of the credential, encrypted on write and masked on read.
    """

    secret = ProtectedSecretField(required=True, allow_null=False)

    class Meta:
        """Serializer configuration for the credentials."""

        model = Authentication
        fields = ("id", "name", "secret", "type", "target_port")
