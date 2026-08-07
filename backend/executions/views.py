"""Endpoints to review the executions and to download their reports."""

from django.db.models import BooleanField, Case, When
from django.http import FileResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from executions.enums import Status
from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from framework.views import BaseViewSet
from rekono.settings import CONFIG
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class ExecutionViewSet(BaseViewSet):
    """List the executions and download the reports of their tools.

    Attributes:
        queryset: All the executions, restricted to the projects of the user by the
          base viewset, and annotated with whether they already started.
        serializer_class: Serializer of the executions.
        filterset_class: Filters available to search executions.
        permission_classes: Role permissions plus the membership in the project.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results, including
          the started annotation, so the executions that didn't start are grouped
          together.
        http_method_names: GET only, since the executions are created by the tasks.
    """

    queryset = Execution.objects.all().annotate(
        started=Case(When(start__isnull=False, then=True), default=False, output_field=BooleanField())
    )
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    search_fields = [
        "task__target__target",
        "task__process__name",
        "configuration__tool__name",
        "configuration__name",
    ]
    ordering_fields = [
        "id",
        "task",
        "configuration",
        "configuration__tool",
        "creation",
        "enqueued_at",
        "start",
        "started",
        "end",
    ]
    http_method_names = ["get"]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description="Execution report file"),
            404: None,
        },
    )
    @action(detail=True, methods=["GET"], url_path="report", url_name="report")
    def download_report(self, request: Request, pk: str) -> FileResponse:
        """Download the report file that the tool of a completed execution wrote.

        Args:
            request: Request that asks for the report.
            pk: Identifier of the execution, taken from the URL.

        Returns:
            The report file, a validation error when the execution isn't completed,
            or a not found response when the tool didn't write any report.
        """
        execution = self.get_object()
        if execution.status != Status.COMPLETED:
            return Response({"execution": "Execution is not completed"}, status=HTTP_400_BAD_REQUEST)
        path = CONFIG.reports / (execution.output_file or "")
        if not execution.output_file or not path.is_file():
            return Response(status=HTTP_404_NOT_FOUND)
        return FileResponse(
            path.open("rb"),
            as_attachment=True,
            filename=f"execution-{execution.id}-{execution.configuration.tool.name.replace(' ', '_')}.{execution.configuration.tool.output_format}",
            status=HTTP_200_OK,
        )
