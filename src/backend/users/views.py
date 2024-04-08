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
from rest_framework_simplejwt.authentication import JWTAuthentication
from security.authorization.permissions import (
    IsAdmin,
    IsNotAuthenticated,
    RekonoModelPermission,
)
from users.filters import UserFilter
from users.models import User
from users.serializers import (
    CreateUserSerializer,
    DisableMfaSerializer,
    EnableMfaSerializer,
    InviteUserSerializer,
    ProfileSerializer,
    RegisterMfaSerializer,
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
    http_method_names = ["get", "post", "put", "delete"]

    def _get_object_if_not_current_user(self, request) -> User:
        instance = self.get_object()  # Get user instance
        if instance.id == request.user.id:
            raise PermissionDenied()
        return instance

    def _is_valid(self, serializer: Serializer, request: Request) -> Serializer:
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer

    def _create(self, serializer: Serializer, request: Request) -> Response:
        serializer = self._is_valid(serializer, request)
        return Response(
            UserSerializer(serializer.create(serializer.validated_data)).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=InviteUserSerializer, responses={201: UserSerializer})
    def create(self, request, *args, **kwargs):
        return self._create(InviteUserSerializer, request)

    @extend_schema(request=CreateUserSerializer, responses={201: UserSerializer})
    @action(
        detail=False,
        methods=["POST"],
        url_path="create",
        permission_classes=[IsNotAuthenticated],
    )
    def create_after_invitation(self, request: Request, *args, **kwargs) -> Response:
        return self._create(CreateUserSerializer, request)

    @extend_schema(
        request=RequestPasswordResetSerializer, responses={200: None}, methods=["POST"]
    )
    @extend_schema(
        request=ResetPasswordSerializer, responses={200: None}, methods=["PUT"]
    )
    @action(
        detail=False,
        methods=["POST", "PUT"],
        url_path="reset-password",
        permission_classes=[IsNotAuthenticated],
    )
    def reset_password(self, request: Request, *args, **kwargs) -> Response:
        serializer = self._is_valid(
            RequestPasswordResetSerializer
            if request.method.lower() == "post"
            else ResetPasswordSerializer,
            request,
        )
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @extend_schema(request=UpdateRoleSerializer, responses={201: UserSerializer})
    def update(self, request, *args, **kwargs):
        instance = self._get_object_if_not_current_user(request)
        serializer = self._is_valid(UpdateRoleSerializer, request)
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
    @action(detail=True, methods=["POST"])
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


class BaseProfileViewSet(GenericViewSet):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    # Only IsAuthenticated class is required because all users can manage its profile
    permission_classes = [IsAuthenticated]

    def _get(self, request: Request) -> Response:
        return Response(
            self.serializer_class(request.user, many=False).data,
            status=status.HTTP_200_OK,
        )

    def _update(self, request: Request, serializer_class: Serializer) -> Serializer:
        serializer = serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return serializer


class ProfileViewSet(BaseProfileViewSet):
    @action(detail=False, methods=["GET"])
    def get_profile(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._get(request)

    @action(detail=False, methods=["PUT"])
    def update_profile(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self._update(request, self.serializer_class)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=UpdatePasswordSerializer, responses={200: None})
    @action(detail=False, methods=["PUT"])
    def update_password(self, request: Request) -> Response:
        self._update(request, UpdatePasswordSerializer)
        return Response(status=status.HTTP_200_OK)


class MfaViewSet(BaseProfileViewSet):
    authentication_classes = [JWTAuthentication]

    @extend_schema(request=None, responses={200: RegisterMfaSerializer})
    @action(detail=False, methods=["POST"])
    def register(self, request: Request, *args, **kwargs) -> Response:
        if request.user.mfa:
            return Response(
                {"mfa": "MFA is already enabled"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            RegisterMfaSerializer(
                {"url": User.objects.register_mfa(request.user)}
            ).data,
            status=status.HTTP_200_OK,
        )

    def _update_mfa(self, request: Request, serializer: Serializer) -> None:
        serializer = serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

    @extend_schema(request=EnableMfaSerializer, responses={200: ProfileSerializer})
    @action(detail=False, methods=["POST"])
    def enable(self, request: Request) -> Response:
        for condition, message in [
            (request.user.mfa, "MFA is already enabled"),
            (not request.user.secret, "MFA is not regiesterd yet"),
        ]:
            if condition:
                return Response({"mfa": message}, status=status.HTTP_400_BAD_REQUEST)
        self._update_mfa(request, EnableMfaSerializer)
        return self._get(request)

    @extend_schema(request=DisableMfaSerializer, responses={200: ProfileSerializer})
    @action(detail=False, methods=["POST"])
    def disable(self, request: Request) -> Response:
        if not request.user.mfa:
            return Response(
                {"mfa": "MFA is already disabled"}, status=status.HTTP_400_BAD_REQUEST
            )
        self._update_mfa(request, DisableMfaSerializer)
        return self._get(request)
