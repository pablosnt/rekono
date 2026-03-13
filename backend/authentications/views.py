"""Django REST framework views for authentication models.

Provides REST API views for authentication records with CRUD operations
and proper authentication and authorization controls.
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

    Provides REST API endpoints for managing authentication records with
    filtering, searching, and ordering capabilities. Enforces project-based
    authorization and user authentication.

    Attributes:
        queryset (QuerySet): Authentication model instances
        serializer_class (Serializer): Serializer for Authentication model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods (GET, POST, DELETE)
    """

    queryset = Authentication.objects.all()
    serializer_class = AuthenticationSerializer
    filterset_class = AuthenticationFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission
    ]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "type"]
    http_method_names = ["get", "post", "delete"]
