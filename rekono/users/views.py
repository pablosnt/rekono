from rest_framework.views import APIView
from users.models import User
from users.serializers import InviteUserSerializer, CreateUserSerializer
from rest_framework.response import Response
from rest_framework import status

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
