"""Viewset of the integration endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from integrations.filters import IntegrationFilter
from integrations.models import Integration
from integrations.serializers import IntegrationSerializer
from security.authorization.permissions import RekonoModelPermission


class IntegrationViewSet(BaseViewSet):
    """Read the external platforms and enable or disable them.

    Attributes:
        queryset: All the integrations, since they aren't tied to any project.
        serializer_class: Serializer of the integrations.
        filterset_class: Filters of the integrations.
        permission_classes: Any user can read the integrations, but only the ones
          that can change them are able to enable or disable them.
        search_fields: Free text search over the name and the description.
        ordering_fields: Fields that the integrations can be sorted by.
        http_method_names: GET and PUT only, since the integrations come from the
          fixtures.
    """

    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    filterset_class = IntegrationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "enabled"]
    http_method_names = ["get", "put"]
