from typing import Generic
from urllib.request import Request

from defectdojo.api import DefectDojo
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from settings.filters import SettingFilter
from settings.models import Setting
from settings.serializers import SettingSerializer

# Create your views here.


class SettingViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin):
    queryset = Setting.objects.all().order_by('-id')
    serializer_class = SettingSerializer
    filterset_class = SettingFilter
    search_fields = ['field']
    http_method_names = ['get', 'put']
    # Required to remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)
    
    @extend_schema(request=None, responses={200: None, 204: None})
    @action(detail=False, methods=['GET'], url_path='defectdojo', url_name='defectdojo')
    def defectdojo(self, request: Request) -> Response:
        dd_client = DefectDojo()
        if dd_client.is_available():
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
