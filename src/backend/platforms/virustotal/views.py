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
    """REST API viewset for VirusTotal platform configuration management.

    Provides secure REST API endpoints for managing VirusTotal platform
    settings and configuration. Supports read and update operations for
    platform credentials and settings with proper authentication controls.

    Attributes:
        queryset: QuerySet for VirusTotalSettings objects
        serializer_class: Serializer for platform settings data
        permission_classes: Authentication and authorization requirements
        http_method_names: Allowed HTTP methods (GET, PUT only)
    """

    queryset = VirusTotalSettings.objects.all()
    serializer_class = VirusTotalSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
