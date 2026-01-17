"""Django REST framework serializers for authentication workflows.

Provides serializer classes for user authentication including login validation,
multi-factor authentication processing, and JWT token management. These serializers
implement secure authentication workflows with comprehensive validation and logging.
"""

from typing import Any

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import CharField, Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from framework.logging import LoggingEntity
from platforms.mail.notifications import SMTP
from rekono.settings import CONFIG
from security.authentication.tokens import MfaRequiredToken
from security.authorization.roles import Role
from users.models import User


class JwtAuthentication(LoggingEntity):
    """Base class for JWT authentication and token management.

    Provides core JWT authentication functionality including token generation,
    user login processing, and security logging. This class serves as the
    foundation for various authentication workflows in the system.

    Security Features:
        - Previous tokens invalidation on new login
        - Role-based JWT claims for authorization
        - Comprehensive authentication logging
        - Email notifications for login events
        - MFA token generation for multi-factor workflows

    Attributes:
        user (User): The authenticated user instance (default: None).
    """

    user: User = None

    def login(self) -> dict[str, str]:
        """Process user login and generate JWT tokens.

        Invalidates all existing tokens for security, generates new access
        and refresh tokens with role-based claims, sends login notification,
        and logs the authentication event.

        Returns:
            dict[str, str]: Dictionary containing 'access' and 'refresh' JWT tokens.
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
        """Generate JWT token with role-based claims.

        Creates a new JWT token pair with embedded role information
        from the user's primary group membership. Defaults to READER
        role if no group is assigned.

        Args:
            user (User): The user for whom to generate tokens.

        Returns:
            Any: JWT token pair with role claims embedded.
        """
        token = TokenObtainPairSerializer.get_token(user)
        group = user.groups.first()
        token["role"] = group.name if group else Role.READER.value
        return token

    @classmethod
    def get_mfa_required_token(cls, user: User) -> Any:
        """Generate temporary MFA token for multi-factor authentication.

        Creates a temporary token that allows access only to MFA completion
        endpoints. This token is issued during the first authentication step
        for MFA-enabled users.

        Args:
            user (User): The user requiring MFA completion.

        Returns:
            Any: Temporary MFA token for authentication completion.
        """
        return MfaRequiredToken.for_user(user)


class LoginSerializer(JwtAuthentication, TokenObtainSerializer):
    """Serializer for primary user authentication with MFA detection.

    Handles the first step of user authentication by validating credentials
    and determining whether MFA is required. For MFA-enabled accounts,
    returns a temporary token; otherwise, completes authentication immediately.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate credentials and handle MFA routing.

        Performs credential validation and routes the authentication flow
        based on the user's MFA settings. Returns either a temporary MFA
        token or complete JWT tokens.

        Args:
            attrs (dict[str, Any]): Authentication attributes (username, password).

        Returns:
            dict[str, Any]: Either MFA token or complete JWT token pair.
        """
        super().validate(attrs)
        return {"mfa": str(self.__class__.get_mfa_required_token(self.user))} if self.user.mfa else self.login()


class MfaSerializer(Serializer):
    """Base serializer for multi-factor authentication validation.

    Provides common MFA validation functionality for TOTP codes, and email
    OTP codes. This base class handles the validation logic shared across
    different MFA completion workflows.

    Attributes:
        mfa (CharField): The MFA code to validate (max 200 characters).
        validator (callable): User model method for MFA validation.
    """

    mfa = CharField(max_length=200, required=True, write_only=True)
    validator = User.objects.verify_mfa_or_otp

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate MFA code against user's configured methods.

        Verifies the provided MFA code using the user's configured
        authentication methods including TOTP or email OTP.

        Args:
            attrs (dict[str, Any]): Validation attributes including MFA code.

        Returns:
            dict[str, Any]: Validated attributes.

        Raises:
            AuthenticationFailed: If MFA code validation fails.
        """
        attrs = super().validate(attrs)
        if not self.validator(
            attrs.get("mfa"),
            (self.user if hasattr(self, "user") and getattr(self, "user") else self.context.get("request").user),
        ):
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs


class MfaRequiredSerializer(Serializer):
    """Base serializer for operations requiring MFA validation.

    Validates temporary MFA tokens and ensures users have MFA enabled.
    This serializer is used for operations that require completion of
    the MFA authentication flow.

    Attributes:
        token (CharField): Temporary MFA token for user identification.
    """

    token = CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate MFA token and verify user MFA status.

        Validates the temporary MFA token, identifies the associated user,
        and verifies that MFA is enabled for the account.

        Args:
            attrs (dict[str, Any]): Validation attributes including MFA token.

        Returns:
            dict[str, Any]: Validated attributes with user context.

        Raises:
            AuthenticationFailed: If token validation fails.
            ValidationError: If MFA is not enabled for the user.
        """
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


class SendMfaEmailSerializer(MfaRequiredSerializer):
    """Serializer for sending MFA codes via email.

    Handles email delivery of one-time passwords for MFA completion when
    TOTP devices are unavailable. Supports both authenticated and
    unauthenticated requests for account recovery scenarios.

    Attributes:
        token (CharField): Optional MFA token for unauthenticated requests.
    """

    token = CharField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate request and determine user context.

        Validates the request context and determines whether the user is
        authenticated or requires token-based identification for MFA email delivery.

        Args:
            attrs (dict[str, Any]): Validation attributes.

        Returns:
            dict[str, Any]: Validated attributes with user context.

        Raises:
            ValidationError: If token is missing for unauthenticated requests.
        """
        is_authenticated = IsAuthenticated().has_permission(self.context.get("request"), None)
        if not is_authenticated and not attrs.get("token"):
            raise ValidationError("Token is required", code="token")
        elif is_authenticated:
            self.user = self.context.get("request").user
        return super().validate(attrs)

    def save(self, **kwargs: Any) -> User:
        """Generate and send OTP via email.

        Creates a time-limited OTP code and sends it to the user's
        registered email address through the SMTP notification system.

        Args:
            **kwargs (Any): Additional save parameters.

        Returns:
            User: The user for whom the OTP was generated.
        """
        SMTP().mfa(self.user, User.objects.setup_otp(self.user, {"minutes": CONFIG.mfa_expiration_minutes}))
        return self.user


class MfaLoginSerializer(MfaSerializer, MfaRequiredSerializer, JwtAuthentication):
    """Serializer for completing MFA authentication and issuing tokens.

    Combines MFA validation, token verification, and JWT generation to complete
    the multi-factor authentication flow. Validates MFA codes and issues
    full JWT tokens upon successful authentication.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Complete MFA validation and authentication.

        Validates the MFA code, cleans up any temporary OTP codes,
        and completes the authentication process by issuing JWT tokens.

        Args:
            attrs (dict[str, Any]): Validation attributes including MFA code.

        Returns:
            dict[str, Any]: Complete JWT token pair (access and refresh tokens).
        """
        super().validate(attrs)
        if self.user.otp:
            User.objects.remove_otp(self.user)
        return self.login()
