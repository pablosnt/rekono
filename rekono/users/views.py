from rest_framework import status
from rest_framework.mixins import (ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from users.models import User
from users.serializers import (ChangeUserRoleSerializer, CreateUserSerializer,
                               InviteUserSerializer, UserSerializer)

# Create your views here.


class InviteUserView(APIView):

    def post(self, request, format=None):
        serializer = InviteUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(APIView):

    def post(self, request, pk, format=None):
        serializer = CreateUserSerializer(data=request.data, context={'pk': pk})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserRoleView(APIView):

    def put(self, request, pk, format=None):
        serializer = ChangeUserRoleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(pk=pk)
                serializer.update(user, serializer.validated_data)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DisableUserView(APIView):

    def post(self, request, pk, format=None):
        try:
            user = User.objects.get(pk=pk, is_active=True)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        User.objects.disable_user(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
