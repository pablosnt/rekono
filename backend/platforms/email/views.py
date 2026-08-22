"""Viewset of the SMTP endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.email.models import SMTPSettings
from platforms.email.serializers import SMTPSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class SMTPSettingsViewSet(BaseViewSet):
    """Read and update the SMTP configuration.

    Attributes:
        queryset: The only settings instance, created by the migrations.
        serializer_class: Serializer of the SMTP settings.
        permission_classes: Only the users that can change the settings model.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = SMTPSettings.objects.all()
    serializer_class = SMTPSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
