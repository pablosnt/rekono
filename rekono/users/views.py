import logging
from typing import Any, List

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import (BasePermission, DjangoModelPermissions,
                                        IsAuthenticated)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from security.authorization.permissions import IsAdmin, IsNotAuthenticated

from users.filters import UserFilter
from users.models import User
from users.serializers import (ChangeUserPasswordSerializer,
                               ChangeUserRoleSerializer, CreateUserSerializer,
                               InviteUserSerializer,
                               RequestPasswordResetSerializer,
                               ResetPasswordSerializer, TelegramBotSerializer,
                               UserProfileSerializer, UserSerializer)

# Create your views here.

logger = logging.getLogger()                                                    # Rekono logger


class UserAdminViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):
    '''User administration ViewSet that includes: get, retrieve, invite, role change, enable and disable features.'''

    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-id')
    filterset_class = UserFilter
    # Fields used to search tasks
    search_fields = ['username', 'first_name', 'last_name', 'email']
    # Required to include the IsAdmin to the base authorization classes and remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions, IsAdmin]

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        '''Disable user.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        instance = self.get_object()
        if instance.is_active is None:
            super().destroy(request, *args, **kwargs)
        else:
            User.objects.disable_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=InviteUserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=['POST'], url_path='invite', url_name='invite')
    def invite(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        '''Invite new user.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        serializer = InviteUserSerializer(data=request.data)
        if serializer.is_valid():                                               # Check input data
            user = serializer.create(serializer.validated_data)                 # Invite user
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid input data

    @extend_schema(request=ChangeUserRoleSerializer, responses={200: UserSerializer})
    @action(detail=True, methods=['PUT'], url_path='role', url_name='role')
    def change_user_role(self, request: Request, pk: str) -> Response:
        '''Change user role.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        '''
        user = self.get_object()                                                # Get user instance
        serializer = ChangeUserRoleSerializer(data=request.data)
        if serializer.is_valid():                                               # Check input data
            serializer.update(user, serializer.validated_data)                  # Change user role
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid input data

    @extend_schema(request=None, responses={200: UserSerializer})
    @action(detail=True, methods=['POST'], url_path='enable', url_name='enable')
    def enable_user(self, request: Request, pk: str) -> Response:
        '''Enable disabled user.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        '''
        user = self.get_object()                                                # Get user instance
        User.objects.enable_user(user)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class UserProfileViewSet(GenericViewSet):
    '''User profile ViewSet that includes: get, update, password change and Telegram bot configuration features.'''

    serializer_class = UserProfileSerializer
    queryset = User.objects.all().order_by('-id')
    # Only IsAuthenticated class is required because all users can manage its profile
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def get_profile(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        '''Get user profile.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        return Response(self.serializer_class(request.user, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'])
    def update_profile(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        '''Update user profile.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        serializer = self.serializer_class(request.user, data=request.data)
        if serializer.is_valid():                                               # Check input data
            serializer.update(request.user, serializer.validated_data)          # Update user profile
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid input data

    @extend_schema(request=ChangeUserPasswordSerializer, responses={200: None})
    @action(detail=False, methods=['PUT'], url_path='change-password', url_name='change-password')
    def change_password(self, request: Request) -> Response:
        '''Change user password.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        serializer = ChangeUserPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid():                                               # Check input data
            serializer.update(request.user, serializer.validated_data)          # Update user password
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid input data

    @extend_schema(request=TelegramBotSerializer, responses={200: None})
    @action(detail=False, methods=['POST'], url_path='telegram-token', url_name='telegram-token')
    def telegram_token(self, request: Request) -> Response:
        '''Link Telegram bot to the user account.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        serializer = TelegramBotSerializer(request.user, data=request.data)
        if serializer.is_valid():                                               # Check input data
            serializer.update(request.user, serializer.validated_data)          # Link Telegram bot to user account
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid input data


class CreateUserViewSet(GenericViewSet):
    '''User ViewSet that includes user initialization from invitation feature.'''

    serializer_class = CreateUserSerializer
    queryset = User.objects.all().order_by('-id')
    # Only IsNotAuthenticated class is required because, users can be initialized from another user session
    permission_classes = [IsNotAuthenticated]

    @action(detail=False, methods=['POST'])
    def create(self, request: Request) -> Response:
        '''User creation from invitation.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():                                               # Check input data
            serializer.save()                                                   # Initialize user data
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid input data


class ResetPasswordViewSet(GenericViewSet):
    '''User ViewSet that includes reset password feature.'''

    queryset = User.objects.all().order_by('-id')
    # No class required because all users can reset his password
    # This operation can be performed from an user session or not
    permission_classes: List[BasePermission] = []

    @extend_schema(request=RequestPasswordResetSerializer, responses={200: None})
    def create(self, request: Request) -> Response:
        '''Request user password reset.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():                                               # Check input data
            try:
                serializer.save()                                               # Request password reset
            except User.DoesNotExist:
                # Ignore User not found errors to prevent user enumeration vulnerabilities
                pass
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid input data

    @extend_schema(request=ResetPasswordSerializer, responses={200: None})
    @action(detail=False, methods=['PUT'])
    def reset_password(self, request: Request) -> Response:
        '''Reset user password.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():                                               # Check input data
            serializer.save()                                                   # Reset password
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid input data
