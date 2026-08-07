"""Base viewsets of the finding endpoints."""

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
    """Base viewset to list the findings and to fix them.

    Attributes:
        permission_classes: Role permissions plus the membership in the project.
        http_method_names: GET to read the findings, and POST and DELETE for the
          fix action, since the findings themselves are only created by the tools.
    """

    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    http_method_names = ["get", "post", "delete"]

    @extend_schema(exclude=True)
    def create(self, request: Request, *args, **kwargs):
        """Reject the creation of findings, which only the executions report.

        Args:
            request: Request that is rejected without being read.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 405 response.
        """
        return self._method_not_allowed("POST")  # pragma: no cover

    @extend_schema(exclude=True)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Reject the deletion of findings, which are fixed instead of removed.

        Args:
            request: Request that is rejected without being read.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 405 response.
        """
        return self._method_not_allowed("DELETE")  # pragma: no cover

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["POST", "DELETE"])
    def fix(self, request: Request, pk: str) -> Response:
        """Mark a finding as fixed with POST, or as not fixed anymore with DELETE.

        Args:
            request: Request whose method decides the new state of the finding,
              and whose user is recorded as the one that fixed it.
            pk: Identifier of the finding, taken from the URL.

        Returns:
            An empty response, or a validation error when a finding that is already
            fixed is fixed again, when one that isn't fixed at all is unfixed, or
            when the one being unfixed was fixed by Rekono instead of by a user,
            since only a new execution can decide that it's there again.
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
    """Base viewset of the findings that the auditors review one by one.

    Attributes:
        http_method_names: Adds PUT to the ones of the base viewset, which is how
          the triage of a finding is updated.
    """

    http_method_names = ["get", "put", "post", "delete"]
