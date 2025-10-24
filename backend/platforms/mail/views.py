"""Django REST framework views for SMTP settings management.

Provides REST API endpoints for SMTP configuration management with proper
authentication and authorization controls. Supports GET and PUT operations
for viewing and updating SMTP server settings.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.mail.models import SMTPSettings
from platforms.mail.serializers import SMTPSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class SMTPSettingsViewSet(BaseViewSet):
    """ViewSet for SMTP settings configuration management.

    Provides REST API endpoints for viewing and updating SMTP server configuration
    settings with proper authentication and authorization controls. Restricts access
    to authenticated users with appropriate permissions.

    Attributes:
        queryset (QuerySet): SMTPSettings model instances
        serializer_class (Serializer): Serializer for SMTP settings
        permission_classes (list): Required permissions for access control
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = SMTPSettings.objects.all()
    serializer_class = SMTPSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
