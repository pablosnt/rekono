from typing import Any, Dict

from authentications.models import Authentication
from framework.fields import ProtectedSecretField
from rest_framework.serializers import ModelSerializer
from security.input_validation import Regex, Validator


class AuthenticationSerializer(ModelSerializer):
    """Serializer to manage authentications via API."""

    secret = ProtectedSecretField(
        Validator(Regex.SECRET.value, code="secret").__call__,
        required=True,
        allow_null=False,
    )

    class Meta:
        """Serializer metadata."""

        model = Authentication
        fields = (
            "id",
            "target_port",
            "name",
            "secret",
            "type",
        )
