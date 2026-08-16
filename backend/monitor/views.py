"""Viewset of the monitor endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from monitor.models import MonitorSettings
from monitor.serializers import MonitorSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class MonitorSettingsViewSet(BaseViewSet):
    """Read and update the configuration of the monitor job.

    Attributes:
        queryset: The only settings instance, created by the migrations.
        serializer_class: Serializer of the monitor settings.
        permission_classes: Only the users that can change the settings model.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = MonitorSettings.objects.all()
    serializer_class = MonitorSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
