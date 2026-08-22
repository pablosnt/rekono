"""Authentication based on the API tokens used by the external clients."""

from typing import Any

from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from api_tokens.models import ApiToken
from security.cryptography import Crypto


class ApiAuthentication(TokenAuthentication):
    """Authentication backend for the requests with an API token.

    Attributes:
        model: Model where the API tokens are stored, already hashed.
    """

    model = ApiToken

    def authenticate_credentials(self, key) -> tuple[Any, Any]:
        """Get the user and the API token that match a token value.

        Args:
            key: Value of the API token, as the client sent it.

        Returns:
            The user that owns the token and the token itself.

        Raises:
            AuthenticationFailed: If no token matches the hashed key, the token's
                user is inactive, or the token has passed its expiration date.
        """
        user, token = super().authenticate_credentials(Crypto.hash(key))
        # A token with no expiration date (expiration is None) never expires
        if token.expiration and token.expiration < timezone.now():
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return user, token
