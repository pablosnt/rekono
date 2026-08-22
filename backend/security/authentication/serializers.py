"""Serializers that implement the login and MFA flows.

A login without MFA is completed by LoginSerializer, and one with MFA is split in
two steps: LoginSerializer issues the temporary MFA token, and MfaLoginSerializer
verifies the code and issues the final tokens. The MFA validation is also reused by
the serializers that enable and disable MFA for an authenticated user.
"""

from typing import Any

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import CharField, Serializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings

from framework.logging import LoggingEntity
from platforms.email.notifications import SMTP
from rekono.settings import CONFIG
from security.authentication.tokens import MfaRequiredToken
from security.authorization.roles import Role
from users.enums import OtpScope
from users.models import User


class JwtAuthentication(LoggingEntity):
    """Issuer of the JWT tokens that a user authenticates with.

    Attributes:
        user: User being logged in, set by the serializers that validate their
          credentials.
    """

    user: User = None

    def login(self) -> dict[str, str]:
        """Complete the login of the user and get their new tokens.

        The tokens issued by previous logins are invalidated, so a login always
        leaves one single valid session, and the user is notified by email.

        Returns:
            The new access and refresh tokens of the user.
        """
        User.objects.invalidate_all_tokens(self.user)
        token = self.__class__.get_token(self.user)
        self.user.last_login = timezone.now()
        self.user.save(update_fields=["last_login"])
        SMTP().login_notification(self.user)
        self.logger.info(f"[Security] User {self.user.id} has logged in", extra={"user": self.user.id})
        return {"access": str(token.access_token), "refresh": str(token)}

    @classmethod
    def get_token(cls, user: User) -> Any:
        """Get a new token pair for a user, including their role as a claim.

        The role claim lets the frontend know what the user can do without asking
        for it, and defaults to Reader for the users without a group.

        Args:
            user: User that the tokens are issued for.

        Returns:
            The refresh token, whose access_token attribute holds the access one.
        """
        token = TokenObtainPairSerializer.get_token(user)
        group = user.groups.first()
        token["role"] = group.name if group else Role.READER.value
        return token

    @classmethod
    def get_mfa_required_token(cls, user: User) -> Any:
        """Get the temporary token that lets a user complete their MFA login.

        Args:
            user: User whose credentials were already validated.

        Returns:
            The MFA token, which only allows completing the login and is
            blacklisted once it's used.
        """
        return MfaRequiredToken.for_user(user)


class LoginSerializer(JwtAuthentication, TokenObtainSerializer):
    """Serializer that validates the username and the password of a user."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the credentials and get the tokens that the user needs next.

        Args:
            attrs: Username and password sent by the client.

        Returns:
            The access and refresh tokens, or only the temporary MFA token when the
            user has MFA enabled and the login isn't complete yet.
        """
        super().validate(attrs)
        return {"mfa": str(self.__class__.get_mfa_required_token(self.user))} if self.user.mfa else self.login()


class MfaSerializer(Serializer):
    """Base serializer that validates an MFA code.

    Attributes:
        mfa: Code to be validated, either the TOTP one or an OTP sent by email.
        validator: User method that verifies the code.
    """

    mfa = CharField(max_length=200, required=True, write_only=True)
    validator = User.objects.verify_mfa_or_otp

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the MFA code against the TOTP secret or the OTP of the user.

        If self.user is already set, as it is for MfaLoginSerializer via
        MfaRequiredSerializer earlier in the MRO, that user is validated. Otherwise,
        as for EnableMfaSerializer and DisableMfaSerializer, self.user is not set and
        the user is instead taken from the authenticated request in the serializer
        context.

        Args:
            attrs: Validated data, including the MFA code.

        Returns:
            The same validated data, unchanged.

        Raises:
            AuthenticationFailed: If the code isn't valid for that user.
        """
        attrs = super().validate(attrs)
        if not self.validator(
            attrs.get("mfa"),
            (self.user if hasattr(self, "user") and getattr(self, "user") else self.context.get("request").user),
        ):
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs


class MfaRequiredSerializer(Serializer):
    """Base serializer that identifies a user in the middle of an MFA login.

    Attributes:
        token: Temporary MFA token that identifies the user that is logging in.
    """

    token = CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the MFA token and that the user has MFA enabled.

        If no token is provided, self.user is expected to already be set by the
        caller, such as an authenticated request in a subclass.

        Args:
            attrs: Validated data, which may include the temporary MFA token.

        Returns:
            The same validated data, unchanged. The identified user is kept in
            self.user for the rest of the flow.

        Raises:
            AuthenticationFailed: If the token is invalid, expired, blacklisted, or
              identifies a user that doesn't exist.
            ValidationError: If MFA isn't enabled for that user.
        """
        attrs = super().validate(attrs)
        if attrs.get("token"):
            try:
                # Validate the token's signature, expiry, token_type and blacklist state
                self.token = MfaRequiredToken(attrs.get("token"))
                self.token.check_blacklist()
                self.user = User.objects.get(id=self.token[api_settings.USER_ID_CLAIM])
            except (TokenError, User.DoesNotExist):
                raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        if not self.user.mfa:
            raise ValidationError("MFA is not enabled yet for this user", code="mfa")
        return attrs


class SendMfaEmailSerializer(MfaRequiredSerializer):
    """Serializer that sends the MFA code by email to a user.

    Attributes:
        token: MFA token, not required at the field level. Custom validation
          requires it for unauthenticated requests and ignores it when the
          requester is already authenticated.
    """

    token = CharField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Identify the user, either by the request they authenticated or by the token.

        Args:
            attrs: Validated data, which includes the MFA token for the anonymous
              requests and can omit it for the authenticated ones.

        Returns:
            The same validated data, unchanged.

        Raises:
            ValidationError: If an anonymous request doesn't include the MFA token.
        """
        is_authenticated = IsAuthenticated().has_permission(self.context.get("request"), None)
        if not is_authenticated and not attrs.get("token"):
            raise ValidationError("Token is required", code="token")
        elif is_authenticated:
            self.user = self.context.get("request").user
        return super().validate(attrs)

    def save(self, **kwargs: Any) -> User:
        """Send a new one-time password to the email address of the user.

        The OTP is bound to the MFA scope, so it can only be used as a second
        factor and not to reset the password or activate the account.

        Args:
            **kwargs: Standard serializer arguments, unused here because the user is
              already identified during the validation.

        Returns:
            The user that received the one-time password.
        """
        plain_otp = User.objects.setup_otp(self.user, OtpScope.MFA, {"minutes": CONFIG.mfa_expiration_minutes})
        SMTP().mfa(self.user, plain_otp)
        return self.user


class MfaLoginSerializer(MfaSerializer, MfaRequiredSerializer, JwtAuthentication):
    """Serializer that completes an MFA login and issues the tokens of the user."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the MFA code and complete the login of the user.

        Args:
            attrs: Temporary MFA token and the MFA code to verify.

        Returns:
            The access and refresh tokens of the user.
        """
        super().validate(attrs)
        # Blacklist the MFA token so it cannot be reused
        self.token.blacklist()
        if self.user.otp:
            User.objects.remove_otp(self.user)
        return self.login()
