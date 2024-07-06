from typing import Any

from api_tokens.models import ApiToken
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from security.cryptography.hashing import hash


class ApiAuthentication(TokenAuthentication):
    model = ApiToken

    def authenticate_credentials(self, key) -> tuple[Any, Any]:
        user, token = super().authenticate_credentials(hash(key))
        if token.expiration and token.expiration < timezone.now():
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return user, token
