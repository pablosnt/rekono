"""Django REST framework views for VulnCheck platform management.

Provides REST API endpoints for managing VulnCheck platform settings and
Bearer token configuration with proper authentication and authorization.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.vulncheck.models import VulnCheckSettings
from platforms.vulncheck.serializers import VulnCheckSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class VulnCheckSettingsViewSet(BaseViewSet):
    """ViewSet for managing VulnCheck platform configuration.

    Provides REST API endpoints for retrieving and updating VulnCheck platform
    settings including Bearer token management and availability status.

    Attributes:
        queryset (QuerySet): All VulnCheckSettings objects
        serializer_class (Serializer): Serializer for settings operations
        permission_classes (list): Required permissions for access
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = VulnCheckSettings.objects.all()
    serializer_class = VulnCheckSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
