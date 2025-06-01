from framework.views import BaseViewSet
from platforms.cvecrowd.models import CveCrowdSettings
from platforms.cvecrowd.serializers import CveCrowdSettingsSerializer
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import RekonoModelPermission


class CveCrowdSettingsViewSet(BaseViewSet):
    queryset = CveCrowdSettings.objects.all()
    serializer_class = CveCrowdSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
