from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from security.serializers import (LogoutSerializer,
                                  RekonoTokenObtainPairSerializer)


class RekonoTokenObtainPairView(TokenObtainPairView):
    serializer_class = RekonoTokenObtainPairSerializer


class LogoutView(GenericViewSet, CreateModelMixin):
    queryset = None
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    @extend_schema(responses={200: None})
    def create(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
