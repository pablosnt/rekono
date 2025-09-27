"""Django REST framework views for CVE Crowd platform management.

Provides REST API endpoints for managing CVE Crowd integration settings
with secure configuration management and platform availability validation
for threat intelligence integration.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.cvecrowd.models import CveCrowdSettings
from platforms.cvecrowd.serializers import CveCrowdSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class CveCrowdSettingsViewSet(BaseViewSet):
    """ViewSet for managing CVE Crowd platform integration settings.

    Provides REST API endpoints for CVE Crowd configuration management
    with secure credential handling and platform availability validation.
    Supports GET and PUT operations for viewing and updating settings.

    Attributes:
        queryset (QuerySet): All CveCrowdSettings objects
        serializer_class (Serializer): CveCrowdSettingsSerializer for settings operations
        permission_classes (list): Required permissions for access control
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = CveCrowdSettings.objects.all()
    serializer_class = CveCrowdSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
