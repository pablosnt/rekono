import logging
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from security.serializers import (LogoutSerializer,
                                  RekonoTokenObtainPairSerializer)

logger = logging.getLogger()                                                    # Rekono logger


class RekonoTokenObtainPairView(TokenObtainPairView):
    '''Token ViewSet that includes the user login (get access and refresh token).'''

    serializer_class = RekonoTokenObtainPairSerializer
    throttle_scope = 'login'


class RekonoTokenRefreshView(TokenRefreshView):
    '''Token ViewSet that includes the refresh access token feature.'''

    throttle_scope = 'refresh'


class LogoutView(GenericViewSet, CreateModelMixin):
    '''Logout ViewSet that includes the user logout feature.'''

    queryset = None
    permission_classes = (IsAuthenticated,)                                     # Any authenticated user can logout
    serializer_class = LogoutSerializer

    @extend_schema(responses={200: None})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        '''Perform the user logout.

        Args:
            request (Request): HTTP request

        Returns:
            Response: HTTP response
        '''
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()                                                   # Perform logout
            logger.info(f'[Security] User {request.user.id} has logged out', extra={'user': request.user.id})
            return Response(status=status.HTTP_200_OK)                          # Logged out
        return Response(status=status.HTTP_400_BAD_REQUEST)                     # Valid refresh token is required
