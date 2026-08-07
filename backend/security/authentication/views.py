"""Endpoints that authenticate the users and manage their JWT tokens.

All of them accept the tokens in the request body, as the standard simplejwt views
do, and also in the cookies where the frontend keeps them, so the browsers complete
the flows without the frontend having to read any token.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

from rekono.settings import CONFIG, COOKIES_CONFIG, JWT_ACCESS_COOKIE, JWT_MFA_COOKIE, JWT_REFRESH_COOKIE
from security.authentication.jwt import CookieJWTAuthentication
from security.authentication.serializers import MfaLoginSerializer, SendMfaEmailSerializer
from security.authorization.permissions import IsNotAuthenticated


class LoginView(TokenObtainPairView):
    """Authenticate a user with their username and password.

    Attributes:
        permission_classes: Only the anonymous users can log in.
        throttle_scope: Rate limit that makes brute force attacks unfeasible.
    """

    permission_classes = [IsNotAuthenticated]
    throttle_scope = "login"

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Log a user in and save their tokens in ``httponly`` cookies.

        Users with MFA enabled get the temporary MFA token instead, in a cookie
        scoped to the MFA endpoint, so it can't be sent to any other one.

        Args:
            request: Request with the username and the password.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            The tokens, which are also saved in the cookies, so the frontend never
            has to read them.
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
    """Complete a login with the MFA code of the user.

    Attributes:
        serializer_class: Validates the MFA code against the MFA token.
        throttle_scope: Rate limit that protects the six digits of the code from
          being brute forced.
    """

    serializer_class = MfaLoginSerializer
    throttle_scope = "mfa"

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Verify the MFA code and issue the access and refresh tokens.

        The MFA token is read from the cookie when the request body doesn't include
        it, and its cookie is removed once the login is complete.

        Args:
            request: Request with the MFA code, and optionally the MFA token.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            The access and refresh tokens, which are also saved in the cookies.
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
    """Send the MFA code by email to the users without their device.

    Attributes:
        permission_classes: None, since the user is in the middle of a login and
          isn't authenticated yet.
        throttle_scope: Same rate limit as the MFA login.
    """

    permission_classes = []
    throttle_scope = "mfa"

    @extend_schema(request=SendMfaEmailSerializer, responses={204: None})
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Send a one-time password to the email address of the user.

        Args:
            request: Request with the MFA token, which can also come from the
              ``rekono_mfa`` cookie, or an authenticated request without it.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            An empty 204 response, since the code is only sent by email.

        Raises:
            AuthenticationFailed: If the MFA token from the request body or the
              ``rekono_mfa`` cookie is invalid, expired, or blacklisted.
            ValidationError: If no token is provided for an unauthenticated request,
              or if MFA is not enabled for the resolved user.
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
    """End a session by blacklisting its refresh token."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Blacklist the refresh token and delete the authentication cookies.

        The refresh token is read from the cookie when the request body doesn't
        include it.

        Args:
            request: Request with the refresh token, which can also come from the
              ``rekono_refresh`` cookie.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            The response of the blacklist view, with the authentication cookies
            already removed.
        """
        if not request.data.get("refresh"):
            cookie = request.COOKIES.get(JWT_REFRESH_COOKIE)
            if cookie:
                request._full_data = {"refresh": cookie}
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            CookieJWTAuthentication.clear_cookies(response)
        return response


class RefreshTokenViewSet(TokenRefreshView):
    """Renew the access token of a session.

    Attributes:
        throttle_scope: Rate limit applied to the renewals, independent from the
          one of the logins.
    """

    throttle_scope = "refresh"

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get a new pair of tokens and save them in the cookies.

        The refresh token is read from the cookie when the request body doesn't
        include it, so the body takes precedence when both are present.

        Args:
            request: Request with the refresh token, which can also come from the
              ``rekono_refresh`` cookie.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            The new tokens, which are also saved in the cookies.

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
