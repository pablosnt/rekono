"""Django REST framework views for monitor settings management.

Provides REST API endpoints for viewing and updating the monitoring
configuration used by the background monitoring jobs.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from monitor.models import MonitorSettings
from monitor.serializers import MonitorSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class MonitorSettingsViewSet(BaseViewSet):
    """ViewSet for managing monitoring settings.

    Provides REST API endpoints for viewing and updating monitoring
    configuration settings. Supports GET and PUT operations only.

    Attributes:
        queryset (QuerySet): All MonitorSettings objects
        serializer_class (Serializer): Serializer for monitor settings
        permission_classes (list): Required permissions for access
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = MonitorSettings.objects.all()
    serializer_class = MonitorSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
