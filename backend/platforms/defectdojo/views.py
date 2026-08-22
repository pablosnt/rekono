"""Viewsets of the DefectDojo endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync
from platforms.defectdojo.serializers import DefectDojoSettingsSerializer, DefectDojoSyncSerializer
from security.authorization.permissions import ProjectMemberPermission, RekonoModelPermission


class DefectDojoSettingsViewSet(BaseViewSet):
    """Read and update the DefectDojo configuration.

    Attributes:
        queryset: The only settings instance, created by the migrations.
        serializer_class: Serializer of the DefectDojo settings.
        permission_classes: Only the users that can change the settings model.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = DefectDojoSettings.objects.all()
    serializer_class = DefectDojoSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]


class DefectDojoSyncViewSet(BaseViewSet):
    """Synchronize a project with DefectDojo, or stop synchronizing it.

    Attributes:
        queryset: All the synchronizations, filtered later by project membership.
        serializer_class: Serializer of the synchronizations.
        permission_classes: Role permissions plus the membership in the project.
        http_method_names: POST and DELETE only, since a synchronization that
          changes is a different one, and the project can read it in its own data.
    """

    queryset = DefectDojoSync.objects.all()
    serializer_class = DefectDojoSyncSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    http_method_names = ["post", "delete"]
