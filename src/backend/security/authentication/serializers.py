import logging
from typing import Any, Dict

from platforms.mail.notifications import SMTP
from rest_framework.serializers import CharField, Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from security.authorization.roles import Role
from users.models import User

logger = logging.getLogger()  # Rekono logger


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        SMTP().login_notification(self.user)
        logger.info(
            f"[Security] User {self.user.id} has logged in",
            extra={"user": self.user.id},
        )
        return attrs

    @classmethod
    def get_token(cls, user: User) -> Dict[str, Any]:
        token = super().get_token(user)  # Get standard claims
        group = user.groups.first()
        token["role"] = group.name if group else Role.READER.value
        return token


class LogoutSerializer(Serializer):
    """Serializer to user logout via API."""

    refresh_token = CharField(max_length=500, required=True)

    def save(self, **kwargs: Any) -> None:
        """Perform the logout operation, including the refresh token in the blacklist."""
        token = RefreshToken(self.validated_data.get("refresh_token"))
        token.blacklist()  # Add refresh token to the blacklist
