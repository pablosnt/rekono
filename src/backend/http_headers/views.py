"""Django REST framework views for HTTP header models.

This module provides REST API views for HTTP header records, including
list, create, retrieve, update, and delete operations with proper
authentication and authorization controls.
"""

from django.db.models import Q, QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from framework.views import BaseViewSet
from http_headers.filters import HttpHeaderFilter
from http_headers.models import HttpHeader
from http_headers.serializers import HttpHeaderSerializer, SimpleHttpHeaderSerializer
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class HttpHeaderViewSet(BaseViewSet):
    """ViewSet for HttpHeader model CRUD operations.

    This ViewSet provides REST API endpoints for managing HTTP header
    records with proper filtering, searching, and ordering capabilities.
    It enforces authentication and project-based authorization, with
    custom queryset filtering for user-specific access control.

    Attributes:
        queryset: QuerySet for HttpHeader model instances.
        serializer_class: Serializer class for HttpHeader model.
        filterset_class: Filter class for query filtering.
        permission_classes: List of permission classes for access control.
        search_fields: Fields available for text search.
        ordering_fields: Fields available for result ordering.
        http_method_names: Allowed HTTP methods for this ViewSet.
    """

    queryset = HttpHeader.objects.all()
    serializer_class = HttpHeaderSerializer
    filterset_class = HttpHeaderFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    search_fields = ["key", "value"]
    ordering_fields = ["id", "target", "user", "key"]
    http_method_names = ["get", "put", "post", "delete"]

    def get_queryset(self) -> QuerySet:
        """Get filtered queryset based on user permissions.

        This method implements custom filtering to ensure users can only
        access HTTP headers they own or headers associated with targets
        they have access to through project membership.

        Returns:
            QuerySet: Filtered queryset containing only accessible headers.
        """
        # Filter to show only user's own headers or headers from projects they're members of
        # This ensures proper data isolation and access control
        return self.queryset.filter(Q(user=self.request.user) | Q(user__isnull=True)).filter(
            Q(target__project__members=self.request.user) | Q(target__isnull=True)
        )

    def get_serializer_class(self) -> Serializer:
        """Get appropriate serializer class based on HTTP method.

        Returns:
            Serializer: The appropriate serializer class for the request.
        """
        # Use simplified serializer for PUT operations (updates)
        # Use full serializer for other operations
        return SimpleHttpHeaderSerializer if self.request.method == "PUT" else super().get_serializer_class()
