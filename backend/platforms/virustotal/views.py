"""Viewset of the VirusTotal endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.virustotal.models import VirusTotalSettings
from platforms.virustotal.serializers import VirusTotalSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class VirusTotalSettingsViewSet(BaseViewSet):
    """Read and update the VirusTotal configuration.

    Attributes:
        queryset: The only settings instance, created by the migrations.
        serializer_class: Serializer of the VirusTotal settings.
        permission_classes: Only the users that can change the settings model.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = VirusTotalSettings.objects.all()
    serializer_class = VirusTotalSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
