from framework.views import BaseViewSet
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import RekonoModelPermission
from settings.models import Settings
from settings.serializers import SettingsSerializer

# Create your views here.


class SettingsViewSet(BaseViewSet):
    """System ViewSet that includes: retrieve and update features."""

    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
