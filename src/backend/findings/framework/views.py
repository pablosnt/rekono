from typing import Any

from drf_spectacular.utils import extend_schema
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


class FindingViewSet(BaseViewSet):
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    # "post" and "delete" are needed to allow finding fixes
    http_method_names = ["get", "post", "delete"]

    @extend_schema(exclude=True)
    def create(self, request: Request, *args, **kwargs):
        return self._method_not_allowed("POST")  # pragma: no cover

    @extend_schema(exclude=True)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._method_not_allowed("DELETE")  # pragma: no cover

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["POST", "DELETE"], url_path="fix", url_name="fix")
    def fix(self, request: Request, pk: str) -> Response:
        finding = self.get_object()
        bad_request = None
        if request.method == "POST":
            if finding.is_fixed:
                bad_request = "Finding is already fixed"
            else:
                finding.__class__.objects.fix(finding, request.user)
        else:
            if not finding.is_fixed or finding.auto_fixed:
                bad_request = "Finding is not manually fixed"
            else:
                finding.__class__.objects.remove_fix(finding, request.user)
        if bad_request:
            return Response(
                {"finding": bad_request}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TriageFindingViewSet(FindingViewSet):
    # "put" method is needed for triaging
    http_method_names = ["get", "put", "post", "delete"]
