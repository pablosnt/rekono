from rest_framework import status
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from users.models import User
from users.serializers import (ChangeUserPasswordSerializer,
                               ChangeUserRoleSerializer, CreateUserSerializer,
                               EnableUserSerializer, InviteUserSerializer,
                               RequestPasswordResetSerializer,
                               ResetPasswordSerializer, UserSerializer)

# Create your views here.


class UserViewSet(ModelViewSet):
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
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InviteUserSerializer
        else:
            return UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        User.objects.disable_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateUserView(APIView):
    serializer_class = CreateUserSerializer

    def post(self, request, pk):
        serializer = self.serializer_class(data=request.data, context={'pk': pk})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserRoleView(APIView):
    serializer_class = ChangeUserRoleSerializer

    def put(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(pk=pk)
                serializer.update(user, serializer.validated_data)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserPasswordView(APIView):
    serializer_class = ChangeUserPasswordSerializer

    def put(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'user': self.request.user}
        )
        if serializer.is_valid():
            serializer.update(self.request.user, serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordView(APIView):
    serializer_class = RequestPasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer_class(request)(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            try:
                serializer.save()
            except User.DoesNotExist:
                pass
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer

    def put(self, request):
        serializer = self.get_serializer_class(request)(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except User.DoesNotExist:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnableUserView(APIView):
    serializer_class = EnableUserSerializer

    def post(self, request, pk):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                user = User.objects.get(pk=pk, is_active=False)
                serializer.update(user, serializer.validated_data)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
