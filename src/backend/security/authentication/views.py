"""Django REST framework views for authentication endpoints.

Provides REST API endpoints for user authentication including login, multi-factor
authentication, and token management. These views implement secure authentication
workflows with rate limiting and comprehensive audit logging.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from security.authentication.serializers import MfaLoginSerializer, SendMfaEmailSerializer
from security.authorization.permissions import IsNotAuthenticated


class LoginView(TokenObtainPairView):
    """JWT token authentication view with MFA support.

    Handles primary user authentication using username/password credentials.
    For MFA-enabled accounts, returns a temporary MFA token instead of
    full access tokens. Implements rate limiting to prevent brute force attacks.

    Attributes:
        permission_classes (list): Restricts access to unauthenticated users only.
        throttle_scope (str): Rate limiting scope for login attempts.
    """

    permission_classes = [IsNotAuthenticated]
    throttle_scope = "login"


class MfaLoginView(LoginView):
    """Multi-factor authentication completion view.

    Completes the MFA challenge by validating TOTP codes and issuing
    full JWT access tokens. Requires a valid MFA token from the initial
    login step.

    Attributes:
        serializer_class (Serializer): MfaLoginSerializer for MFA validation.
        throttle_scope (str): Rate limiting scope for MFA attempts.
    """

    serializer_class = MfaLoginSerializer
    throttle_scope = "mfa"


class SendEmailMfaView(GenericAPIView):
    """Email-based one-time password delivery view.

    Sends time-limited OTP codes via email for MFA-enabled users who cannot
    access their TOTP device or backup codes. Provides secure account recovery
    mechanism for MFA-protected accounts.

    Attributes:
        permission_classes (list): No authentication required for account recovery.
        throttle_scope (str): Rate limiting scope for MFA email requests.
    """

    permission_classes = []
    throttle_scope = "mfa"

    @extend_schema(request=SendMfaEmailSerializer, responses={204: None})
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Send OTP code via email for MFA completion.

        Generates and sends a time-limited OTP code to the user's registered
        email address for MFA completion when TOTP devices are unavailable.

        Args:
            request (Request): HTTP request with user identification.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Response: HTTP 204 on successful OTP delivery.

        Raises:
            ValidationError: If MFA is not enabled or user validation fails.
        """
        serializer = SendMfaEmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshTokenViewSet(TokenRefreshView):
    """JWT refresh token endpoint for token renewal.

    Provides secure token refresh functionality to obtain new access tokens
    using valid refresh tokens. Implements rate limiting and automatic
    token rotation for enhanced security.

    Attributes:
        throttle_scope (str): Rate limiting scope for token refresh requests.
    """

    throttle_scope = "refresh"
