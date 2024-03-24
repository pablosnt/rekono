from typing import Any

from drf_spectacular.utils import extend_schema
from findings.framework.serializers import FindingSerializer
from framework.views import BaseViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class TriageFindingViewSet(BaseViewSet):
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    # "post" and "delete" are needed to allow finding fixes
    http_method_names = ["get", "put", "post", "delete"]

    @extend_schema(exclude=True)
    def create(self, request: Request, *args, **kwargs):
        return self._method_not_allowed("POST")

    @extend_schema(request=None, responses={200: FindingSerializer})
    @action(detail=True, methods=["POST"], url_path="fix", url_name="fix")
    def fix(self, request: Request, pk: str) -> Response:
        finding = self.get_object()
        if finding.is_fixed:
            return Response(
                {"finding": "Finding is already fixed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        finding = finding.__class__.objects.fix(finding, request.user)
        return Response(
            self.get_serializer_class()(finding).data, status=status.HTTP_200_OK
        )

    @extend_schema(exclude=True)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._method_not_allowed("DELETE")

    @action(detail=True, methods=["DELETE"], url_path="fix", url_name="fix")
    def unfix(self, request: Request, pk: str) -> Response:
        finding = self.get_object()
        if not finding.is_fixed or finding.auto_fixed:
            return Response(
                {"finding": "Finding is not manually fixed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        finding.__class__.objects.unfix(finding, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FindingViewSet(TriageFindingViewSet):
    # Remove "put" method, as it's only used for triaging
    http_method_names = ["get", "post", "delete"]
