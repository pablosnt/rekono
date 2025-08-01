"""Views for the integrations app.

This module provides Django REST Framework views for the Integration model,
enabling API endpoints for integration management and configuration.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from integrations.filters import IntegrationFilter
from integrations.models import Integration
from integrations.serializers import IntegrationSerializer
from security.authorization.permissions import RekonoModelPermission


class IntegrationViewSet(BaseViewSet):
    """ViewSet for managing Integration model instances.

    This ViewSet provides API endpoints for listing, retrieving, and updating
    Integration instances. It supports filtering, searching, and ordering
    capabilities while enforcing proper authentication and authorization.

    The ViewSet restricts HTTP methods to GET and PUT operations, allowing
    users to view integration details and update their enabled status, but
    preventing creation or deletion of integrations through the API.

    Attributes:
        queryset: All Integration instances.
        serializer_class: IntegrationSerializer for data conversion.
        filterset_class: IntegrationFilter for query filtering.
        permission_classes: Authentication and authorization requirements.
        search_fields: Fields that can be searched via the API.
        ordering_fields: Fields that can be used for result ordering.
        http_method_names: Allowed HTTP methods (GET, PUT only).
    """

    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    filterset_class = IntegrationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "enabled"]
    http_method_names = ["get", "put"]
