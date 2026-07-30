"""Django REST Framework views for VirusTotal platform configuration.

This module provides REST API viewsets for managing VirusTotal platform
configuration and settings. Supports secure configuration management with
proper authentication and authorization controls.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.virustotal.models import VirusTotalSettings
from platforms.virustotal.serializers import VirusTotalSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class VirusTotalSettingsViewSet(BaseViewSet):
    """ViewSet for managing VirusTotal platform configuration.

    Provides REST API endpoints for retrieving and updating VirusTotal
    platform settings including token management and availability status.

    Attributes:
        queryset (QuerySet): All VirusTotalSettings objects
        serializer_class (Serializer): Serializer for settings operations
        permission_classes (list): Required permissions for access
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = VirusTotalSettings.objects.all()
    serializer_class = VirusTotalSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
