from typing import Any, Tuple

from api_tokens.models import ApiToken
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from security.utils.cryptography import hash


class ApiAuthentication(TokenAuthentication):
    model = ApiToken

    def authenticate_credentials(self, key):
        return super().authenticate_credentials(hash(key))

    def authenticate_credentials(self, key) -> Tuple[Any, Any]:
        user, token = super().authenticate_credentials(hash(key))
        if token.expiration and token.expiration < timezone.now():
            raise AuthenticationFailed("API token has expired")
        return user, token
