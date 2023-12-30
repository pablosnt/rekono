from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from security.authorization.permissions import IsNotAuthenticated


class LoginViewSet(TokenObtainPairView):
    """Token ViewSet that includes the user login (get access and refresh token)."""

    permission_classes = [IsNotAuthenticated]  # type: ignore
    throttle_scope = "login"


class RefreshTokenViewSet(TokenRefreshView):
    """Token ViewSet that includes the refresh access token feature."""

    throttle_scope = "refresh"
