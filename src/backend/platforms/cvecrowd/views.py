from framework.views import BaseViewSet
from platforms.cvecrowd.models import CVECrowdSettings
from platforms.cvecrowd.serializers import CVECrowdSettingsSerializer
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import RekonoModelPermission


class CVECrowdSettingsViewSet(BaseViewSet):
    queryset = CVECrowdSettings.objects.all()
    serializer_class = CVECrowdSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
