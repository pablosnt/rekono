"""Settings views for Rekono API.

This module provides REST API views for managing global system settings
through secure, permission-controlled endpoints. It implements administrative
access to platform configuration with proper authentication and authorization.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import RekonoModelPermission
from settings.models import Settings
from settings.serializers import SettingsSerializer


class SettingsViewSet(BaseViewSet):
    """ViewSet for managing global system settings through REST API.

    Provides secure administrative access to platform configuration settings
    through GET and PUT operations. Enforces proper authentication and
    model-level permissions for configuration management.

    The ViewSet restricts access to authenticated administrators with appropriate
    permissions and limits HTTP methods to read and update operations only.

    Attributes:
        queryset: All Settings model instances for administrative access.
        serializer_class: SettingsSerializer for data validation and serialization.
        permission_classes: Authentication and model permission requirements.
        http_method_names: Restricted to GET and PUT operations for security.
    """

    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
