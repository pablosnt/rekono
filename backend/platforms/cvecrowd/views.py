"""Viewset of the CVE Crowd endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.cvecrowd.models import CveCrowdSettings
from platforms.cvecrowd.serializers import CveCrowdSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class CveCrowdSettingsViewSet(BaseViewSet):
    """Read and update the CVE Crowd configuration.

    Attributes:
        queryset: The only settings instance, created from a fixture.
        serializer_class: Serializer of the CVE Crowd settings.
        permission_classes: Only the users that can change the settings model.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = CveCrowdSettings.objects.all()
    serializer_class = CveCrowdSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
