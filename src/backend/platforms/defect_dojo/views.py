from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from framework.views import BaseViewSet
from platforms.defect_dojo.models import DefectDojoSettings, DefectDojoSync
from platforms.defect_dojo.serializers import (
    DefectDojoEngagementSerializer,
    DefectDojoProductSerializer,
    DefectDojoProductTypeSerializer,
    DefectDojoSettingsSerializer,
    DefectDojoSyncSerializer,
)
from security.authorization.permissions import (
    IsAuditor,
    ProjectMemberPermission,
    RekonoModelPermission,
)

# Create your views here.


class DefectDojoSettingsViewSet(BaseViewSet):
    queryset = DefectDojoSettings.objects.all()
    serializer_class = DefectDojoSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = [
        "get",
        "put",
    ]


class DefectDojoSyncViewSet(BaseViewSet):
    queryset = DefectDojoSync.objects.all()
    serializer_class = DefectDojoSyncSerializer
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    http_method_names = [
        "post",
        "delete",
    ]


class DefectDojoEntityViewSet(BaseViewSet):
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated, IsAuditor]

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer_class()(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        try:
            response = serializer.create(serializer.validated_data)
            return Response({"id": response.get("id")}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(
                {"defect-dojo": "Error creating instance on Defect-Dojo"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DefectDojoProductTypeViewSet(DefectDojoEntityViewSet):
    serializer_class = DefectDojoProductTypeSerializer


class DefectDojoProductViewSet(DefectDojoEntityViewSet):
    serializer_class = DefectDojoProductSerializer


class DefectDojoEngagementViewSet(DefectDojoEntityViewSet):
    serializer_class = DefectDojoEngagementSerializer
