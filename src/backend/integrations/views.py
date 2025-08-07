"""Django REST framework views for integration management.

Provides REST API endpoints for managing third-party integrations.
Includes ViewSets for read-only operations and enabling/disabling integrations.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from integrations.filters import IntegrationFilter
from integrations.models import Integration
from integrations.serializers import IntegrationSerializer
from security.authorization.permissions import RekonoModelPermission


class IntegrationViewSet(BaseViewSet):
    """ViewSet for managing third-party integration configurations.

    Provides REST API endpoints for integration read operations and status updates.
    Supports filtering by name and enabled status with search capabilities.

    Attributes:
        queryset (QuerySet): All Integration objects
        serializer_class (Serializer): Default serializer for integration operations
        filterset_class (FilterSet): Filter class for querying integrations
        permission_classes (list): Required permissions for access
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    filterset_class = IntegrationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "enabled"]
    http_method_names = ["get", "put"]
