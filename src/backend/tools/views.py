from typing import Any

from drf_spectacular.utils import extend_schema
from framework.views import BaseViewSet, LikeViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from security.authorization.permissions import RekonoModelPermission
from tools.filters import ConfigurationFilter, ToolFilter
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, ToolSerializer

# Create your views here.


class ToolViewSet(LikeViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    filterset_class = ToolFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name", "command"]
    ordering_fields = ["id", "name", "command"]
    # "post" and "delete" are needed to allow POST requests to like and dislike tools
    http_method_names = ["get", "post", "delete"]

    @extend_schema(exclude=True)
    def create(self, request: Request, *args, **kwargs) -> Response:
        return self._method_not_allowed("POST")  # pragma: no cover

    @extend_schema(exclude=True)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._method_not_allowed("DELETE")    # pragma: no cover


class ConfigurationViewSet(BaseViewSet):
    """Configuration ViewSet that includes: get and retrieve features."""

    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    filterset_class = ConfigurationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name"]
    http_method_names = ["get"]
