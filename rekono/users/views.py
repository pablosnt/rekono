from typing import List

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import (BasePermission, DjangoModelPermissions,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from security.authorization.permissions import IsAdmin
from users.filters import UserFilter
from users.models import User
from users.serializers import (ChangeUserPasswordSerializer,
                               ChangeUserRoleSerializer, CreateUserSerializer,
                               EnableUserSerializer, InviteUserSerializer,
                               RequestPasswordResetSerializer,
                               ResetPasswordSerializer,
                               TelegramTokenSerializer, UserProfileSerializer,
                               UserSerializer)

# Create your views here.


class UserAdminViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_class = UserFilter
    search_fields = ['username', 'first_name', 'last_name', 'username', 'email']
    permission_classes: List[BasePermission] = [IsAuthenticated, DjangoModelPermissions, IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        User.objects.disable_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=InviteUserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=['POST'], url_path='invite', url_name='invite')
    def invite(self, request, *args, **kwargs):
        serializer = InviteUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            response = UserSerializer(user)
            return Response(response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=ChangeUserRoleSerializer, responses={200: UserSerializer})
    @action(detail=True, methods=['PUT'], url_path='role', url_name='role')
    def change_user_role(self, request, pk):
        user = self.get_object()
        serializer = ChangeUserRoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            response = UserSerializer(user)
            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=EnableUserSerializer, responses={200: UserSerializer})
    @action(detail=True, methods=['POST'], url_path='enable', url_name='enable')
    def enable_user(self, request, pk):
        user = self.get_object()
        serializer = EnableUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            response = UserSerializer(user)
            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(GenericViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes: List[BasePermission] = [IsAuthenticated]
    http_method_names = ['get', 'put', 'post']

    @action(detail=False, methods=['GET'])
    def get_profile(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'])
    def update_profile(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data)
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=ChangeUserPasswordSerializer, responses={200: None})
    @action(detail=False, methods=['PUT'], url_path='change-password', url_name='change-password')
    def change_password(self, request):
        serializer = ChangeUserPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=TelegramTokenSerializer, responses={200: None})
    @action(detail=False, methods=['POST'], url_path='telegram-token', url_name='telegram-token')
    def telegram_token(self, request):
        serializer = TelegramTokenSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInitViewSet(GenericViewSet):
    serializer_class = CreateUserSerializer
    queryset = User.objects.all()
    permission_classes: List[BasePermission] = []
    http_method_names = ['post']

    @action(detail=False, methods=['POST'])
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordViewSet(GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes: List[BasePermission] = []
    http_method_names = ['post', 'put']

    @extend_schema(request=RequestPasswordResetSerializer, responses={200: None})
    def create(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
            except User.DoesNotExist:
                pass
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=ResetPasswordSerializer, responses={200: None})
    @action(detail=False, methods=['PUT'])
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except User.DoesNotExist:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
