"""Django REST framework views for tools management and configuration.

Provides REST API views for security tools and configurations with read-only
access, like functionality for tools, and proper authentication controls.
Includes specialized handling for tools that support user interactions.
"""

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
    """ViewSet for security tools management with like functionality.

    Provides REST API endpoints for security tools with read-only access,
    filtering, searching capabilities, and user like/dislike functionality.
    Tools cannot be created or modified through the API.

    Tools whose configurations are all deprecated are excluded, because a tool can
    only be executed through a configuration. Their Tool and Configuration rows are
    still kept in the database, so past executions keep resolving the tool name,
    report format and findings.

    Custom Actions:
        like: Like/unlike tools (inherited from LikeViewSet)

    Attributes:
        queryset (QuerySet): Tool objects with at least one non-deprecated configuration
        serializer_class (Serializer): Serializer for Tool model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods (GET, POST for likes, DELETE for unlikes)
    """

    queryset = Tool.objects.annotate(
        has_active_configurations=Exists(Configuration.objects.filter(tool=OuterRef("pk"), deprecated=False))
    ).filter(has_active_configurations=True)
    serializer_class = ToolSerializer
    filterset_class = ToolFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name", "command", "script"]
    ordering_fields = ["id", "name", "command", "liked", "likes"]
    # "post" and "delete" are needed to allow POST requests to like and dislike tools
    http_method_names = ["get", "post", "delete"]

    @extend_schema(exclude=True)
    def create(self, request: Request, *args, **kwargs) -> Response:
        """Override create to prevent tool creation via API.

        Tools are managed through fixtures and system configuration,
        not user creation.

        Args:
            request (Request): The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: HTTP 405 Method Not Allowed response
        """
        return self._method_not_allowed("POST")  # pragma: no cover

    @extend_schema(exclude=True)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override destroy to prevent tool deletion via API.

        Tools are managed through fixtures and system configuration,
        not user deletion.

        Args:
            request (Request): The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: HTTP 405 Method Not Allowed response
        """
        return self._method_not_allowed("DELETE")  # pragma: no cover


class ConfigurationViewSet(BaseViewSet):
    """ViewSet for tool configurations with read-only access.

    Provides REST API endpoints for tool configurations with filtering
    and searching capabilities. Configurations are read-only and managed
    through fixtures and system configuration.

    Attributes:
        queryset (QuerySet): Non-deprecated Configuration objects
        serializer_class (Serializer): Serializer for Configuration model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        http_method_names (list): Allowed HTTP methods (GET only)
    """

    queryset = Configuration.objects.filter(deprecated=False)
    serializer_class = ConfigurationSerializer
    filterset_class = ConfigurationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name"]
    http_method_names = ["get"]
