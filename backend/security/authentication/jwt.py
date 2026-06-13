"""Cookie-aware JWT authentication backend for Rekono security framework.

Extends the standard simplejwt JWTAuthentication to support access tokens
delivered via named cookies in addition to the Authorization header.
"""

from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """JWT authentication backend that accepts tokens from cookies or headers.

    Extends simplejwt's JWTAuthentication to check the configured access-token
    cookie before falling back to the standard Authorization: Bearer header.
    API token authentication (Authorization: Token) is handled by a separate
    backend and is not affected by this class.

    Priority:
        1. Cookie named ``settings.JWT_ACCESS_COOKIE``
        2. Authorization: Bearer <token> header (default simplejwt behaviour)

    Example:
        Configure in Django settings:

        ```python
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'security.authentication.api.ApiAuthentication',
                'security.authentication.jwt.CookieJWTAuthentication',
            ]
        }
        ```
    """

    def authenticate(self, request):
        """Authenticate the request using a JWT from cookie or header.

        Checks the access-token cookie first. If the cookie is absent, delegates
        to the parent implementation which reads from the Authorization header.
        If the cookie is present but the token is invalid, simplejwt raises
        ``InvalidToken`` which Django REST Framework converts to a 401 response.

        Args:
            request: The incoming HTTP request.

        Returns:
            tuple[User, Token] | None: Authenticated user and validated token,
                or None if no credential is present.

        Raises:
            InvalidToken: If the cookie token fails validation.
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
            response (Response): The response to clear the auth cookies on.

        Returns:
            Response: The same response with both auth cookies deleted.
        """
        response.delete_cookie(settings.JWT_ACCESS_COOKIE)
        response.delete_cookie(settings.JWT_REFRESH_COOKIE, f"{settings.CONFIG.root_path or ''}/api/security/")
        return response
