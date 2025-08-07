"""Django REST framework views for NVD NIST platform management.

Provides REST API endpoints for managing NVD NIST platform settings and
API token configuration with proper authentication and authorization.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.nvdnist.models import NvdNistSettings
from platforms.nvdnist.serializers import NvdNistSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class NvdNistSettingsViewSet(BaseViewSet):
    """ViewSet for managing NVD NIST platform configuration.

    Provides REST API endpoints for retrieving and updating NVD NIST
    platform settings including API token management and availability status.

    Attributes:
        queryset (QuerySet): All NvdNistSettings objects
        serializer_class (Serializer): Serializer for settings operations
        permission_classes (list): Required permissions for access
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = NvdNistSettings.objects.all()
    serializer_class = NvdNistSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
