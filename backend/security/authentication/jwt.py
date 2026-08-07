"""Authentication based on the JWT tokens that the frontend keeps in cookies."""

from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authentication backend for the requests with a JWT access token.

    The token is read from the access token cookie, and from the standard
    ``Authorization: Bearer`` header when that cookie isn't present. The API tokens
    are handled by a different backend, so they aren't affected by this class.
    """

    def authenticate(self, request):
        """Get the user and the access token of the request, if it has one.

        Args:
            request: Request whose access token cookie is read, falling back to the
              ``Authorization`` header.

        Returns:
            The authenticated user and the validated token, or None when the
            request doesn't include any credential.

        Raises:
            InvalidToken: If the cookie token is malformed, expired, or otherwise invalid.
            AuthenticationFailed: If the token's user cannot be resolved or is inactive.
        """
        raw_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE)
        if raw_token is None:
            return super().authenticate(request)
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    @classmethod
    def clear_cookies(cls, response: Response) -> Response:
        """Delete the access and refresh JWT cookies from a response.

        Ends a cookie-based session immediately by removing both auth cookies, using the
        same names and refresh-cookie path the login flow set them with. Shared by logout
        and the password change/reset flows so a credential change kills the current session.

        Args:
            response: Response where the removal of the cookies is instructed.

        Returns:
            The same response, so it can be returned directly by the callers.
        """
        response.delete_cookie(settings.JWT_ACCESS_COOKIE)
        response.delete_cookie(settings.JWT_REFRESH_COOKIE, f"{settings.CONFIG.root_path or ''}/api/security/")
        return response
