"""Viewsets of the tool endpoints."""

from typing import Any

from django.db.models import Exists, OuterRef
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from framework.views import BaseViewSet, LikeViewSet
from security.authorization.permissions import RekonoModelPermission
from tools.filters import ConfigurationFilter, ToolFilter
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, ToolSerializer


class ToolViewSet(LikeViewSet):
    """Read the tools that Rekono can run, and like them.

    Attributes:
        queryset: Tools with at least one configuration that isn't deprecated,
          since a tool can only be run through a configuration. The deprecated
          ones stay in the database so the old executions can still be read.
        serializer_class: Serializer of the tools.
        filterset_class: Filters of the tools.
        permission_classes: Only the users that can read the tools.
        search_fields: Free text search over the tool name and its command.
        ordering_fields: Fields that the tools can be sorted by.
        http_method_names: GET to read the tools, and POST and DELETE for the like
          action, since the tools themselves are created by the migrations.
    """

    queryset = Tool.objects.annotate(
        has_active_configurations=Exists(Configuration.objects.filter(tool=OuterRef("pk"), deprecated=False))
    ).filter(has_active_configurations=True)
    serializer_class = ToolSerializer
    filterset_class = ToolFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name", "command", "script"]
    ordering_fields = ["id", "name", "command", "liked", "likes"]
    http_method_names = ["get", "post", "delete"]

    @extend_schema(exclude=True)
    def create(self, request: Request, *args, **kwargs) -> Response:
        """Reject the creation of tools, which only the migrations define.

        Args:
            request: Request that is rejected without being read.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 405 response.
        """
        return self._method_not_allowed("POST")  # pragma: no cover

    @extend_schema(exclude=True)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Reject the deletion of tools, which only the migrations define.

        Args:
            request: Request that is rejected without being read.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 405 response.
        """
        return self._method_not_allowed("DELETE")  # pragma: no cover


class ConfigurationViewSet(BaseViewSet):
    """Read the things that the tools can do.

    Attributes:
        queryset: Configurations that aren't deprecated, so the users can't pick a
          configuration that won't run anymore.
        serializer_class: Serializer of the configurations.
        filterset_class: Filters of the configurations.
        permission_classes: Only the users that can read the configurations.
        search_fields: Free text search over the configuration name.
        http_method_names: GET only, since the configurations are created by the
          migrations.
    """

    queryset = Configuration.objects.filter(deprecated=False)
    serializer_class = ConfigurationSerializer
    filterset_class = ConfigurationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name"]
    http_method_names = ["get"]
