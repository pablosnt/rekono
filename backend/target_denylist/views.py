"""Django REST framework views for target denylist management.

Provides REST API views for target denylist operations including CRUD
operations and specialized filtering for administrative and user contexts.
"""

from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import RekonoModelPermission
from target_denylist.filters import TargetDenylistFilter
from target_denylist.models import TargetDenylist
from target_denylist.serializers import TargetDenylistSerializer


class TargetDenylistViewSet(BaseViewSet):
    """ViewSet for target denylist management operations.

    Provides REST API endpoints for managing target denylist entries with
    administrative controls and filtering capabilities. Restricts modification
    of default entries to prevent unauthorized changes to system-wide exclusions.

    Attributes:
        queryset (QuerySet): All TargetDenylist objects
        serializer_class (Serializer): TargetDenylistSerializer for data conversion
        filterset_class (FilterSet): TargetDenylistFilter for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods for CRUD operations
    """

    queryset = TargetDenylist.objects.all()
    filterset_class = TargetDenylistFilter
    serializer_class = TargetDenylistSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["target"]
    ordering_fields = ["id", "target", "default"]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self) -> QuerySet:
        """Get filtered queryset based on request method.

        Restricts PUT and DELETE operations to non-default entries only,
        preventing modification of system-wide default denylist entries.
        All other operations can access the complete queryset.

        Returns:
            QuerySet: Filtered queryset excluding default entries for modifications.
        """
        default_queryset = super().get_queryset()
        return (
            default_queryset.filter(default=False).all()
            if self.request.method in ["PUT", "DELETE"]
            else default_queryset
        )
