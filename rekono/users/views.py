from rest_framework.views import APIView
from users.serializers import CreateUserSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site

# Create your views here.


class CreateUserView(APIView):

    def post(self, request, format=None):
        serializer = CreateUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
