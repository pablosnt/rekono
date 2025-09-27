"""API token authentication backend for Rekono security framework.

Provides secure API token authentication with expiration validation and
cryptographic token hashing. This module implements Django REST Framework
authentication backend for API token-based access.
"""

from typing import Any

from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from api_tokens.models import ApiToken
from security.cryptography import Crypto


class ApiAuthentication(TokenAuthentication):
    """API token authentication backend with expiration and hashing support.

    Extends Django REST Framework's TokenAuthentication to provide secure
    API token validation with cryptographic hashing and expiration date
    enforcement. This backend is used for API access authentication.

    Attributes:
        model (type): The ApiToken model class for token storage.

    Example:
        Configure in Django settings:

        ```python
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'security.authentication.api.ApiAuthentication',
            ]
        }
        ```
    """

    model = ApiToken

    def authenticate_credentials(self, key) -> tuple[Any, Any]:
        """Authenticate API token credentials with expiration validation.

        Validates the provided API token by hashing it, looking it up in the
        database, and checking expiration status. Returns the associated user
        and token objects if authentication succeeds.

        Args:
            key (str): The raw API token to authenticate.

        Returns:
            tuple[Any, Any]: Tuple of (user, token) objects for successful authentication.

        Raises:
            AuthenticationFailed: If token is expired or invalid.
        """
        user, token = super().authenticate_credentials(Crypto.hash(key))
        if token.expiration and token.expiration < timezone.now():
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return user, token
