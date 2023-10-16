from framework.views import BaseViewSet
from integrations.defect_dojo.models import DefectDojoSettings, DefectDojoSync
from integrations.defect_dojo.serializers import (
    DefectDojoEngagementSerializer,
    DefectDojoProductSerializer,
    DefectDojoProductTypeSerializer,
    DefectDojoSettingsSerializer,
    DefectDojoSyncSerializer,
)

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


class DefectDojoProductViewSet(BaseViewSet):
    serializer_class = DefectDojoProductSerializer
    http_method_names = ["post"]


class DefectDojoEngagementViewSet(BaseViewSet):
    serializer_class = DefectDojoEngagementSerializer
    http_method_names = ["post"]
