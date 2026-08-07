"""Viewset of the VulnCheck endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.vulncheck.models import VulnCheckSettings
from platforms.vulncheck.serializers import VulnCheckSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class VulnCheckSettingsViewSet(BaseViewSet):
    """Read and update the VulnCheck configuration.

    Attributes:
        queryset: The only settings instance, created from a fixture.
        serializer_class: Serializer of the VulnCheck settings.
        permission_classes: Only the users that can change the settings model.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = VulnCheckSettings.objects.all()
    serializer_class = VulnCheckSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
