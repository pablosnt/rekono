from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from security.authentication.serializers import (
    MfaLoginSerializer,
    SendMfaEmailSerializer,
)
from security.authorization.permissions import IsNotAuthenticated


class LoginView(TokenObtainPairView):
    permission_classes = [IsNotAuthenticated]
    throttle_scope = "login"


class MfaLoginView(LoginView):
    serializer_class = MfaLoginSerializer
    throttle_scope = "mfa"


class SendEmailMfaView(GenericAPIView):
    permission_classes = []
    throttle_scope = "mfa"

    @extend_schema(request=SendMfaEmailSerializer, responses={204: None})
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = SendMfaEmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshTokenViewSet(TokenRefreshView):
    """Token ViewSet that includes the refresh access token feature."""

    throttle_scope = "refresh"
