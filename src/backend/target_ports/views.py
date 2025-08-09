"""Django REST framework views for target port management.

Provides REST API views for target port records with CRUD operations,
filtering capabilities, and project-based authorization controls.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)
from target_ports.filters import TargetPortFilter
from target_ports.models import TargetPort
from target_ports.serializers import TargetPortSerializer


class TargetPortViewSet(BaseViewSet):
    """ViewSet for TargetPort model CRUD operations.

    Provides REST API endpoints for target port management with filtering,
    searching, and ordering capabilities. Enforces project-based authorization
    and user authentication.

    Attributes:
        queryset (QuerySet): TargetPort model instances
        serializer_class (Serializer): Serializer for TargetPort model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods (GET, POST, DELETE)
    """

    queryset = TargetPort.objects.all()
    serializer_class = TargetPortSerializer
    filterset_class = TargetPortFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    search_fields = ["port", "path"]
    ordering_fields = ["id", "target", "port", "path"]
    http_method_names = ["get", "post", "delete"]
