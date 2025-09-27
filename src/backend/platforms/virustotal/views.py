from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.virustotal.models import VirusTotalSettings
from platforms.virustotal.serializers import VirusTotalSettingsSerializer
from security.authorization.permissions import RekonoModelPermission


class VirusTotalSettingsViewSet(BaseViewSet):
    queryset = VirusTotalSettings.objects.all()
    serializer_class = VirusTotalSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
