"""Django REST framework views for target management.

Provides REST API views for target records with CRUD operations,
filtering capabilities, and project-based authorization controls.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import ProjectMemberPermission, RekonoModelPermission
from targets.filters import TargetFilter
from targets.models import Target
from targets.serializers import TargetSerializer


class TargetViewSet(BaseViewSet):
    """ViewSet for Target model CRUD operations.

    Provides REST API endpoints for target management with filtering,
    searching, and ordering capabilities. Enforces project-based authorization
    and user authentication.

    Attributes:
        queryset (QuerySet): Target model instances
        serializer_class (Serializer): Serializer for Target model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods (GET, POST, DELETE)
    """

    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    filterset_class = TargetFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    search_fields = ["target"]
    ordering_fields = ["id", "target", "type"]
    http_method_names = ["get", "post", "delete"]
