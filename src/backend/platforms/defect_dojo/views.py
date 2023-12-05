from framework.views import BaseViewSet
from platforms.defect_dojo.models import DefectDojoSettings, DefectDojoSync
from platforms.defect_dojo.serializers import (
    DefectDojoEngagementSerializer,
    DefectDojoProductSerializer,
    DefectDojoProductTypeSerializer,
    DefectDojoSettingsSerializer,
    DefectDojoSyncSerializer,
)
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import IsAuditor

# Create your views here.


class DefectDojoSettingsViewSet(BaseViewSet):
    queryset = DefectDojoSettings.objects.all()
    serializer_class = DefectDojoSettingsSerializer
    http_method_names = [
        "get",
        "put",
    ]


class DefectDojoSyncViewSet(BaseViewSet):
    queryset = DefectDojoSync.objects.all()
    serializer_class = DefectDojoSyncSerializer
    http_method_names = [
        "post",
        "delete",
    ]


class DefectDojoProductTypeViewSet(BaseViewSet):
    serializer_class = DefectDojoProductTypeSerializer
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated, IsAuditor]


class DefectDojoProductViewSet(BaseViewSet):
    serializer_class = DefectDojoProductSerializer
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated, IsAuditor]


class DefectDojoEngagementViewSet(BaseViewSet):
    serializer_class = DefectDojoEngagementSerializer
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated, IsAuditor]
