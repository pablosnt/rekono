"""Viewset of the NVD NIST endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.nvdnist.models import NvdNistSettings
from platforms.nvdnist.serializers import NvdNistSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class NvdNistSettingsViewSet(BaseViewSet):
    """Read and update the NVD NIST configuration.

    Attributes:
        queryset: The only settings instance, created by the migrations.
        serializer_class: Serializer of the NVD NIST settings.
        permission_classes: Only the users that can change the settings model.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = NvdNistSettings.objects.all()
    serializer_class = NvdNistSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
