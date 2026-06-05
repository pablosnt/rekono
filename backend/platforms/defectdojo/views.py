"""Django REST framework views for DefectDojo integration management.

Provides REST API endpoints for DefectDojo configuration and project synchronization
management with proper authentication and authorization controls.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync
from platforms.defectdojo.serializers import DefectDojoSettingsSerializer, DefectDojoSyncSerializer
from security.authorization.permissions import ProjectMemberPermission, RekonoModelPermission


class DefectDojoSettingsViewSet(BaseViewSet):
    """ViewSet for DefectDojo integration settings management.

    Provides REST API endpoints for viewing and updating DefectDojo integration
    configuration settings with proper authentication and authorization controls.
    Restricts access to authenticated users with appropriate permissions.

    Attributes:
        queryset (QuerySet): DefectDojoSettings model instances
        serializer_class (Serializer): Serializer for DefectDojo settings
        permission_classes (list): Required permissions for access control
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = DefectDojoSettings.objects.all()
    serializer_class = DefectDojoSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]


class DefectDojoSyncViewSet(BaseViewSet):
    """ViewSet for DefectDojo project synchronization management.

    Provides REST API endpoints for creating and deleting DefectDojo project
    synchronization mappings with project-level access control. Enables users
    to establish connections between Rekono projects and DefectDojo entities.

    Attributes:
        queryset (QuerySet): DefectDojoSync model instances
        serializer_class (Serializer): Serializer for DefectDojo synchronization
        permission_classes (list): Required permissions including project membership
        http_method_names (list): Allowed HTTP methods (POST, DELETE only)
    """

    queryset = DefectDojoSync.objects.all()
    serializer_class = DefectDojoSyncSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    http_method_names = ["post", "delete"]
