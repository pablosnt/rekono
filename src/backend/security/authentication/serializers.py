import logging
from typing import Any

from django.core.exceptions import ValidationError
from framework.serializers import MfaSerializer
from platforms.mail.notifications import SMTP
from rekono.settings import CONFIG
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import CharField, Serializer
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from security.authentication.tokens import MfaRequiredToken
from security.authorization.roles import Role
from users.models import User

logger = logging.getLogger()


class JwtAuthentication:
    user: User = None

    def _login(self) -> dict[str, str]:
        User.objects.invalidate_all_tokens(self.user)
        token = self.__class__.get_token(self.user)
        SMTP().login_notification(self.user)
        logger.info(
            f"[Security] User {self.user.id} has logged in",
            extra={"user": self.user.id},
        )
        return {"access": str(token.access_token), "refresh": str(token)}

    @classmethod
    def get_token(cls, user: User) -> Any:
        token = TokenObtainPairSerializer.get_token(user)
        group = user.groups.first()
        token["role"] = group.name if group else Role.READER.value
        return token

    @classmethod
    def get_mfa_required_token(cls, user: User) -> Any:
        return MfaRequiredToken.for_user(user)


class LoginSerializer(JwtAuthentication, TokenObtainSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        super().validate(attrs)
        return (
            {"mfa": str(self.__class__.get_mfa_required_token(self.user))}
            if self.user.mfa
            else self._login()
        )


class BaseMfaRequiredSerializer(Serializer):
    token = CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        if attrs.get("token"):
            try:
                self.token = OutstandingToken.objects.get(token=attrs.get("token"))
                self.user = self.token.user
            except Exception:
                raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        if not self.user.mfa:
            raise ValidationError("MFA is not enabled yet for this user", code="mfa")
        return attrs


class SendMfaEmailSerializer(BaseMfaRequiredSerializer):
    token = CharField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        is_authenticated = IsAuthenticated().has_permission(
            self.context.get("request"), None
        )
        if not is_authenticated and not attrs.get("token"):
            raise ValidationError("Token is required", code="token")
        elif is_authenticated:
            self.user = self.context.get("request").user
        return super().validate(attrs)

    def save(self, **kwargs: Any) -> User:
        SMTP().mfa(
            self.user,
            User.objects.setup_otp(
                self.user, {"minutes": CONFIG.mfa_expiration_minutes}
            ),
        )
        return self.user


class MfaLoginSerializer(MfaSerializer, BaseMfaRequiredSerializer, JwtAuthentication):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        super().validate(attrs)
        if self.user.otp:
            User.objects.remove_otp(self.user)
        return self._login()
