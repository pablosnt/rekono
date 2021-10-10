from authorization.permissions import IsAdmin
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from users.models import User
from users.serializers import (ChangeUserPasswordSerializer,
                               ChangeUserRoleSerializer, CreateUserSerializer,
                               EnableUserSerializer, InviteUserSerializer,
                               RequestPasswordResetSerializer,
                               ResetPasswordSerializer, UserSerializer)

# Create your views here.


# Request reset password /reset-password -> "Public"
# Reset password /reset-password -> "Public" based on OTP
# Create POST /id/create -> "Public" based on OTP


class UserAdminViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_fields = {
        'username': ['exact', 'contains'],
        'first_name': ['exact', 'contains'],
        'last_name': ['exact', 'contains'],
        'email': ['exact', 'contains'],
        'is_active': ['exact'],
        'date_joined': ['gte', 'lte', 'exact'],
        'groups': ['exact'],
    }
    ordering_fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined')
    permission_classes = [IsAuthenticated, DjangoModelPermissions, IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = InviteUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            response = UserSerializer(user)
            return Response(response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        User.objects.disable_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put']

    @action(detail=False, methods=['GET'])
    def get_profile(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'])
    def update_profile(self, request):
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


class UserInitViewSet(GenericViewSet):
    serializer_class = CreateUserSerializer
    queryset = User.objects.all()
    permission_classes = []
    http_method_names = ['post']

    @action(detail=True, methods=['POST'])
    def create(self, request, pk):
        serializer = self.serializer_class(data=request.data, context={'pk': pk})
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
    permission_classes = []
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
