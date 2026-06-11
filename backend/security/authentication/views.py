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
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

from rekono.settings import CONFIG, COOKIES_CONFIG, JWT_ACCESS_COOKIE, JWT_MFA_COOKIE, JWT_REFRESH_COOKIE
from security.authentication.serializers import MfaLoginSerializer, SendMfaEmailSerializer
from security.authorization.permissions import IsNotAuthenticated


class LoginView(TokenObtainPairView):
    """JWT token authentication view with MFA support.

    Handles primary user authentication using username/password credentials.
    On success, sets ``httponly`` cookies for the access and refresh tokens so
    browsers carry them automatically on subsequent requests. For MFA-enabled
    accounts a temporary MFA token cookie is set instead, scoped to the MFA
    endpoint path. Implements rate limiting to prevent brute force attacks.

    Attributes:
        permission_classes (list): Restricts access to unauthenticated users only.
        throttle_scope (str): Rate limiting scope for login attempts.
    """

    permission_classes = [IsNotAuthenticated]
    throttle_scope = "login"

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Authenticate and set auth cookies on success.

        Delegates to the parent serializer chain. On HTTP 200 the response
        tokens are written into ``httponly`` cookies: access and refresh tokens
        for standard logins, or an MFA token restricted to ``/api/security/mfa/``
        for accounts with MFA enabled.

        Args:
            request (Request): HTTP request with ``username`` and ``password``.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Response: HTTP 200 with token payload and auth cookies, or the
                upstream error response on failure.
        """
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            if "access" in response.data:
                response.set_cookie(JWT_ACCESS_COOKIE, response.data["access"], **COOKIES_CONFIG)
                response.set_cookie(
                    JWT_REFRESH_COOKIE,
                    response.data["refresh"],
                    path=f"{CONFIG.root_path or ''}/api/security/",
                    **COOKIES_CONFIG,
                )
            elif "mfa" in response.data:
                response.set_cookie(
                    JWT_MFA_COOKIE,
                    response.data["mfa"],
                    path=f"{CONFIG.root_path or ''}/api/security/mfa/",
                    **COOKIES_CONFIG,
                )
        return response


class MfaLoginView(LoginView):
    """Multi-factor authentication completion view.

    Completes the MFA challenge by validating TOTP codes and issuing full JWT
    access tokens. Accepts the MFA token either from the request body or from
    the ``rekono_mfa`` cookie set by ``LoginView``, so the browser can complete
    the flow without the frontend explicitly forwarding the token. Requires a
    valid MFA token from the initial login step.

    Attributes:
        serializer_class (Serializer): MfaLoginSerializer for MFA validation.
        throttle_scope (str): Rate limiting scope for MFA attempts.
    """

    serializer_class = MfaLoginSerializer
    throttle_scope = "mfa"

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Complete MFA login, reading the MFA token from cookie when absent from body.

        If the ``token`` field is not present in the request body, the value is
        read from the ``rekono_mfa`` cookie. On success the MFA cookie is deleted
        and full access and refresh cookies are set via the parent ``LoginView``.

        Args:
            request (Request): HTTP request with ``mfa`` code and optionally ``token``.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Response: HTTP 200 with access token payload and auth cookies on
                success, or the upstream error response on failure.
        """
        if not request.data.get("token"):
            cookie = request.COOKIES.get(JWT_MFA_COOKIE)
            if cookie:
                request._full_data = {"mfa": request.data.get("mfa"), "token": cookie}
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.delete_cookie(JWT_MFA_COOKIE, f"{CONFIG.root_path or ''}/api/security/mfa/")
        return response


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
        if not request.data.get("token"):
            cookie = request.COOKIES.get(JWT_MFA_COOKIE)
            if cookie:
                request._full_data = {"token": cookie}
        serializer = SendMfaEmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(TokenBlacklistView):
    """JWT logout view that blacklists the refresh token and clears auth cookies.

    Accepts the refresh token from the request body or from the cookie named
    ``settings.JWT_REFRESH_COOKIE``. On success, both the access and refresh
    cookies are cleared from the client.
    """

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Blacklist the refresh token and delete auth cookies.

        If the ``refresh`` field is absent from the request body, the value is
        read from the ``rekono_refresh`` cookie. On a successful blacklist both
        ``rekono_access`` and ``rekono_refresh`` cookies are deleted.

        Args:
            request (Request): HTTP request optionally carrying a refresh token
                in the body or in the ``rekono_refresh`` cookie.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Response: HTTP 200 on success with both auth cookies cleared.
        """
        if not request.data.get("refresh"):
            cookie = request.COOKIES.get(JWT_REFRESH_COOKIE)
            if cookie:
                request._full_data = {"refresh": cookie}
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.delete_cookie(JWT_ACCESS_COOKIE)
            response.delete_cookie(JWT_REFRESH_COOKIE, f"{CONFIG.root_path or ''}/api/security/")
        return response


class RefreshTokenViewSet(TokenRefreshView):
    """JWT refresh token endpoint for token renewal.

    Provides secure token refresh functionality to obtain new access tokens
    using valid refresh tokens. Implements rate limiting and automatic
    token rotation for enhanced security.

    Attributes:
        throttle_scope (str): Rate limiting scope for token refresh requests.
    """

    throttle_scope = "refresh"

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Refresh JWT tokens, accepting the refresh token from cookie or body.

        If the ``refresh`` field is absent from the request body, the value is
        read from the cookie named ``settings.JWT_REFRESH_COOKIE``. When
        both are absent, the serializer validation fails with the standard 400
        response. The body takes precedence when both are present.

        Args:
            request (Request): HTTP request optionally carrying a refresh token
                in the body or in the ``rekono_refresh`` cookie.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Response: HTTP 200 with new ``access`` and ``refresh`` token pair.

        Raises:
            InvalidToken: If the refresh token is invalid or blacklisted.
        """
        if not request.data.get("refresh"):
            cookie = request.COOKIES.get(JWT_REFRESH_COOKIE)
            if cookie:
                request._full_data = {"refresh": cookie}
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK and "access" in response.data:
            response.set_cookie(JWT_ACCESS_COOKIE, response.data["access"], **COOKIES_CONFIG)
            response.set_cookie(
                JWT_REFRESH_COOKIE,
                response.data["refresh"],
                path=f"{CONFIG.root_path or ''}/api/security/",
                **COOKIES_CONFIG,
            )
        return response
