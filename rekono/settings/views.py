from typing import Any
from urllib.request import Request

from drf_spectacular.utils import extend_schema
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from settings.models import Setting
from settings.serializers import SettingSerializer

# Create your views here.


class SettingViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    http_method_names = ['get', 'put']
    # Required to remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    @extend_schema(request=None, responses={200: SettingSerializer})
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = SettingSerializer(self.queryset.first(), many=False)
        return Response(serializer.data)
