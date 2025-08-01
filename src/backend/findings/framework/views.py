"""Base ViewSet classes for findings framework.

This module provides the foundational ViewSet classes for the findings system,
including FindingViewSet and TriageFindingViewSet that all specific
finding ViewSets inherit from. These provide standardized functionality
for handling finding operations like fixing and triaging.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class FindingViewSet(BaseViewSet):
    """Base ViewSet for all finding types.

    Provides standardized functionality for finding operations including
    fixing and unfixing findings. Extends BaseViewSet to add finding-specific
    behavior while maintaining security and permission controls.
    """

    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    # "post" and "delete" are needed to allow finding fixes
    http_method_names = ["get", "post", "delete"]

    @extend_schema(exclude=True)
    def create(self, request: Request, *args, **kwargs):
        """Disable creation of findings through API.

        Findings are created automatically by tool executions,
        not manually through the API.
        """
        return self._method_not_allowed("POST")  # pragma: no cover

    @extend_schema(exclude=True)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Disable deletion of findings through API.

        Findings are managed through fixing/unfixing operations,
        not direct deletion.
        """
        return self._method_not_allowed("DELETE")  # pragma: no cover

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["POST", "DELETE"])
    def fix(self, request: Request, pk: str) -> Response:
        """Fix or unfix a finding.

        POST: Mark the finding as fixed by the current user.
        DELETE: Remove the fixed status if it was manually fixed.

        Args:
            request: The HTTP request object.
            pk: Primary key of the finding to fix/unfix.

        Returns:
            Response indicating success or error.
        """
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
            return Response({"finding": bad_request}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TriageFindingViewSet(FindingViewSet):
    """Base ViewSet for findings that support triage.

    Extends FindingViewSet to add triage functionality, allowing
    findings to be marked as false positives, true positives, or
    won't fix with comments and tracking.
    """

    # "put" method is needed for triaging
    http_method_names = ["get", "put", "post", "delete"]
