"""Serializers for API token models with secure key handling.

Provides serialization for API tokens including secure key generation,
hashing, and proper display/creation logic.
"""

from typing import Any

from rest_framework.serializers import ModelSerializer

from api_tokens.models import ApiToken
from security.cryptography import Crypto


class ApiTokenSerializer(ModelSerializer):
    """Serializer for displaying API token information.

    Handles serialization of API token data for display purposes.
    Excludes the actual key for security reasons.
    """

    class Meta:
        """Meta configuration for the ApiTokenSerializer.

        Attributes:
            model (Model): The ApiToken model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = ApiToken
        fields = ("id", "name", "expiration")


class CreateApiTokenSerializer(ModelSerializer):
    """Serializer for creating new API tokens with secure key handling.

    Handles token creation including automatic key generation, hashing for storage,
    and returning the plain key only once during creation.
    """

    class Meta:
        """Meta configuration for the CreateApiTokenSerializer.

        Attributes:
            model (Model): The ApiToken model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified during creation
        """

        model = ApiToken
        fields = ("id", "key", "name", "expiration")
        read_only_fields = ("key",)

    def save(self, **kwargs: Any) -> ApiToken:
        """Save a new API token with a generated and hashed key.

        Generates a unique key, hashes it for database storage, but returns
        the plain key for one-time display to the user.

        Args:
            **kwargs (Any): Additional keyword arguments for saving

        Returns:
            ApiToken: The created API token instance with plain key attached
        """
        plain_key = ApiToken.generate_key()
        self.validated_data["key"] = Crypto.hash(plain_key)
        api_token = super().save(**kwargs)
        api_token.key = plain_key
        return api_token
