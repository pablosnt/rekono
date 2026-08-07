"""Serializers of the API token endpoints."""

from typing import Any

from rest_framework.serializers import ModelSerializer

from api_tokens.models import ApiToken
from security.cryptography import Crypto


class ApiTokenSerializer(ModelSerializer):
    """Serializer of an API token, without its value, which is never exposed."""

    class Meta:
        """Serializer configuration for the API tokens."""

        model = ApiToken
        fields = ("id", "name", "expiration")


class CreateApiTokenSerializer(ModelSerializer):
    """Serializer that creates an API token and returns its value once."""

    class Meta:
        """Serializer configuration for the creation of API tokens."""

        model = ApiToken
        fields = ("id", "key", "name", "expiration")
        read_only_fields = ("key",)

    def save(self, **kwargs: Any) -> ApiToken:
        """Create the API token, storing its hash and returning its plain value.

        Args:
            **kwargs: Extra fields for the token, like the user that the viewset
              adds.

        Returns:
            The new API token, with its plain value in the key field, which is the
            only time that value is available, since the database keeps its hash.
        """
        plain_key = ApiToken.generate_key()
        self.validated_data["key"] = Crypto.hash(plain_key)
        api_token = super().save(**kwargs)
        api_token.key = plain_key
        return api_token
