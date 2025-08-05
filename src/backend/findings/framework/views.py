"""Base ViewSet classes for findings framework REST API.

Provides foundational ViewSet classes including FindingViewSet and
TriageFindingViewSet that all specific finding ViewSets inherit from
with standardized functionality for fixing and triage operations.
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
    """Base ViewSet for all finding types with fixing capabilities.

    Provides standardized REST API functionality for finding operations
    including fixing/unfixing with proper permission controls and
    project-level access restrictions.

    Custom Actions:
        fix: Fix or unfix findings with proper status tracking

    Attributes:
        permission_classes (list): Required permissions for finding access
        http_method_names (list): Allowed HTTP methods for finding operations
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
        """Disable manual finding creation through API.

        Findings are created exclusively through automated tool executions
        and cannot be manually created via API endpoints.

        Args:
            request (Request): HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Method not allowed response.
        """
        return self._method_not_allowed("POST")  # pragma: no cover

    @extend_schema(exclude=True)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Disable direct finding deletion through API.

        Findings are managed through fixing/unfixing lifecycle operations
        rather than direct deletion to preserve audit trails.

        Args:
            request (Request): HTTP request object.
            *args (Any): Variable length argument list.
            **kwargs (Any): Arbitrary keyword arguments.

        Returns:
            Response: Method not allowed response.
        """
        return self._method_not_allowed("DELETE")  # pragma: no cover

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["POST", "DELETE"])
    def fix(self, request: Request, pk: str) -> Response:
        """Fix or unfix a finding with status tracking.

        Handles finding lifecycle management through fix/unfix operations
        with proper user attribution and relationship propagation.

        HTTP Methods:
            POST: Mark finding as fixed by current user.
            DELETE: Remove fixed status if manually fixed.

        Args:
            request (Request): HTTP request object with user context.
            pk (str): Primary key of the finding to modify.

        Returns:
            Response: Success (204) or error (400) response.
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
    """Base ViewSet for findings requiring triage workflow.

    Extends FindingViewSet to add triage functionality enabling findings
    to be classified as false positives, true positives, or won't fix
    with detailed tracking and audit capabilities.

    Attributes:
        http_method_names (list): Allowed HTTP methods including PUT for triage operations
    """

    # "put" method is needed for triaging
    http_method_names = ["get", "put", "post", "delete"]
