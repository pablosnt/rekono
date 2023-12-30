from typing import Tuple
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from security.authorization.permissions import IsNotAuthenticated
from rest_framework.permissions import BasePermission


class LoginViewSet(TokenObtainPairView):
    """Token ViewSet that includes the user login (get access and refresh token)."""

    permission_classes: Tuple[BasePermission] = (IsNotAuthenticated,)
    throttle_scope = "login"


class RefreshTokenViewSet(TokenRefreshView):
    """Token ViewSet that includes the refresh access token feature."""

    throttle_scope = "refresh"
