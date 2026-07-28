"""Settings views for Rekono API.

This module provides REST API views for managing global system settings
through secure, permission-controlled endpoints, with proper authentication
and authorization.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import RekonoModelPermission
from settings.models import Settings
from settings.serializers import SettingsSerializer


class SettingsViewSet(BaseViewSet):
    """ViewSet for managing global system settings through REST API.

    Provides secure access to platform configuration settings through GET
    and PUT operations. Enforces proper authentication and model-level
    permissions for configuration management.

    Settings are readable by any authenticated role, but only administrators
    can update them, and HTTP methods are limited to read and update
    operations only.

    Attributes:
        queryset (QuerySet): All Settings model instances.
        serializer_class (Serializer): SettingsSerializer for data validation and serialization.
        permission_classes (list): Authentication and model permission requirements.
        http_method_names (list): Restricted to GET and PUT operations for security.
    """

    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
