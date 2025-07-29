"""Serializers for API token models, including creation and display logic."""

from typing import Any

from rest_framework.serializers import ModelSerializer

from api_tokens.models import ApiToken
from security.cryptography.hashing import hash


class ApiTokenSerializer(ModelSerializer):
    """Serializer for displaying API token information."""

    class Meta:
        model = ApiToken
        fields = ("id", "name", "expiration")


class CreateApiTokenSerializer(ModelSerializer):
    """Serializer for creating new API tokens, including key generation and hashing."""

    class Meta:
        model = ApiToken
        fields = ("id", "key", "name", "expiration")
        read_only_fields = ("key",)

    def save(self, **kwargs: Any) -> ApiToken:
        """Save a new API token with a generated and hashed key.

        Store the hashed key in the database, but return the plain key to
        the caller. This ensures the plain key is only shown once and
        never stored in plaintext.

        Args:
            **kwargs: Additional keyword arguments for saving.

        Returns:
            ApiToken: The created API token instance with the plain key set.
        """
        plain_key = ApiToken.generate_key()
        self.validated_data["key"] = hash(plain_key)
        api_token = super().save(**kwargs)
        api_token.key = plain_key
        return api_token
