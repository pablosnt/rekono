import logging
from typing import Any

from drf_spectacular.utils import extend_schema
from framework.views import BaseViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from security.authentication.serializers import LoginSerializer, LogoutSerializer
from security.authorization.permissions import IsNotAuthenticated

logger = logging.getLogger()  # Rekono logger


class LoginViewSet(TokenObtainPairView):
    """Token ViewSet that includes the user login (get access and refresh token)."""

    serializer_class = LoginSerializer
    permission_classes = [IsNotAuthenticated]
    throttle_scope = "login"


class RefreshTokenViewSet(TokenRefreshView):
    """Token ViewSet that includes the refresh access token feature."""

    throttle_scope = "refresh"


class LogoutViewSet(BaseViewSet):
    """Logout ViewSet that includes the user logout feature."""

    queryset = None
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "post",
    ]

    @extend_schema(responses={200: None})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)  # Logged out
