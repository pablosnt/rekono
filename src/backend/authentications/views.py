"""Django REST framework views for authentication models.

This module provides REST API views for authentication records, including
list, create, retrieve, update, and delete operations with proper
authentication and authorization controls.
"""

from rest_framework.permissions import IsAuthenticated

from authentications.filters import AuthenticationFilter
from authentications.models import Authentication
from authentications.serializers import AuthenticationSerializer
from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class AuthenticationViewSet(BaseViewSet):
    """ViewSet for Authentication model CRUD operations.

    This ViewSet provides REST API endpoints for managing authentication
    records with proper filtering, searching, and ordering capabilities.
    It enforces authentication and project-based authorization.

    Attributes:
        queryset: QuerySet for Authentication model instances.
        serializer_class: Serializer class for Authentication model.
        filterset_class: Filter class for query filtering.
        permission_classes: List of permission classes for access control.
        search_fields: Fields available for text search.
        ordering_fields: Fields available for result ordering.
        http_method_names: Allowed HTTP methods for this ViewSet.
    """

    queryset = Authentication.objects.all()
    serializer_class = AuthenticationSerializer
    filterset_class = AuthenticationFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "type"]
    http_method_names = ["get", "post", "delete"]
