from framework.views import BaseViewSet
from platforms.nvdnist.models import NvdNistSettings
from platforms.nvdnist.serializers import NvdNistSettingsSerializer
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import RekonoModelPermission


class NvdNistSettingsViewSet(BaseViewSet):
    queryset = NvdNistSettings.objects.all()
    serializer_class = NvdNistSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
