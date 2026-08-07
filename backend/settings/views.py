"""Viewset of the settings endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import RekonoModelPermission
from settings.models import Settings
from settings.serializers import SettingsSerializer


class SettingsViewSet(BaseViewSet):
    """Read and update the Rekono configuration.

    Attributes:
        queryset: The only settings instance, created from a fixture.
        serializer_class: Serializer of the settings.
        permission_classes: Any user can read the settings, but only the ones that
          can change the settings model are able to update them.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
