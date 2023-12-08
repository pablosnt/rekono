import logging
from typing import Any

from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from framework.views import BaseViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from security.authorization.permissions import (
    IsAdmin,
    IsNotAuthenticated,
    RekonoModelPermission,
)
from users.filters import UserFilter
from users.models import User
from users.serializers import (
    CreateUserSerializer,
    InviteUserSerializer,
    ProfileSerializer,
    RequestPasswordResetSerializer,
    ResetPasswordSerializer,
    UpdatePasswordSerializer,
    UpdateRoleSerializer,
    UserSerializer,
)

# Create your views here.

logger = logging.getLogger()


class UserViewSet(BaseViewSet):
    """User administration ViewSet that includes: get, retrieve, invite, role change, enable and disable features."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_class = UserFilter
    # Required to include the IsAdmin to the base authorization classes and remove unneeded permissions
    permission_classes = [IsAuthenticated, RekonoModelPermission, IsAdmin]
    # Fields used to search tasks
    search_fields = ["username", "first_name", "last_name", "email"]
    ordering_fields = [
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "date_joined",
        "last_login",
    ]
    http_method_names = [
        "get",
        "post",
        "put",
        "delete",
    ]

    def _get_object_if_not_current_user(self, request) -> User:
        instance = self.get_object()  # Get user instance
        if instance.id == request.user.id:
            raise PermissionDenied()
        return instance

    @extend_schema(request=InviteUserSerializer, responses={201: UserSerializer})
    def create(self, request, *args, **kwargs):
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(request=UpdateRoleSerializer, responses={201: UserSerializer})
    def update(self, request, *args, **kwargs):
        instance = self._get_object_if_not_current_user(request)
        serializer = UpdateRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.update(instance, serializer.validated_data)
        return Response(UserSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self._get_object_if_not_current_user(request)
        if instance.is_active is None:
            super().destroy(request, *args, **kwargs)
        else:
            User.objects.disable_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={200: UserSerializer})
    @action(detail=True, methods=["POST"], url_path="enable", url_name="enable")
    def enable(self, request: Request, pk: str) -> Response:
        """Enable disabled user.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        """
        instance = self._get_object_if_not_current_user(request)
        User.objects.enable_user(instance)
        return Response(UserSerializer(instance).data, status=status.HTTP_200_OK)


class ProfileViewSet(GenericViewSet):
    """User profile ViewSet that includes: get, update, password change and Telegram bot configuration features."""

    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    # Only IsAuthenticated class is required because all users can manage its profile
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"])
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response(
            self.serializer_class(request.user, many=False).data,
            status=status.HTTP_200_OK,
        )

    def _update(self, request: Request, serializer_class: Serializer) -> Serializer:
        serializer = serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return serializer

    @action(detail=False, methods=["PUT"])
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self._update(request, self.serializer_class)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=UpdatePasswordSerializer, responses={200: None})
    @action(
        detail=False,
        methods=["PUT"],
        url_path="update-password",
        url_name="update-password",
    )
    def update_password(self, request: Request) -> Response:
        self._update(request, UpdatePasswordSerializer)
        return Response(status=status.HTTP_200_OK)


class CreateUserViewSet(GenericViewSet):
    """User ViewSet that includes user initialization from invitation feature."""

    serializer_class = CreateUserSerializer
    queryset = User.objects.all()
    # Users can't be initialized from another user session, authentication is based on OTP
    permission_classes = [IsNotAuthenticated]

    @extend_schema(request=CreateUserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=["POST"])
    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        # headers = self.get_success_headers(serializer.data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class ResetPasswordViewSet(GenericViewSet):
    """User ViewSet that includes reset password feature."""

    queryset = User.objects.all()
    permission_classes = [IsNotAuthenticated]

    def _create_or_update(
        self, request: Request, serializer_class: Serializer
    ) -> Serializer:
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    @extend_schema(request=RequestPasswordResetSerializer, responses={200: None})
    def create(self, request: Request) -> Response:
        self._create_or_update(request, RequestPasswordResetSerializer)
        return Response(status=status.HTTP_200_OK)

    @extend_schema(request=ResetPasswordSerializer, responses={200: None})
    @action(detail=False, methods=["PUT"])
    def update(self, request: Request) -> Response:
        self._create_or_update(request, ResetPasswordSerializer)
        return Response(status=status.HTTP_200_OK)
