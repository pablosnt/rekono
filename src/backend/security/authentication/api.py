from typing import Any, Tuple

from api_tokens.models import ApiToken
from django.utils import timezone
from rekono.settings import CONFIG
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from security.cryptography.hashing import hash


class ApiAuthentication(TokenAuthentication):
    model = ApiToken

    def authenticate_credentials(self, key) -> Tuple[Any, Any]:
        user, token = super().authenticate_credentials(
            hash(f"{key}:{CONFIG.encryption_key}")
        )
        if token.expiration and token.expiration < timezone.now():
            raise AuthenticationFailed("API token has expired")
        return user, token
