"""Django REST framework views for execution models.

This module provides REST API views for execution records, including
list, retrieve operations and report download functionality with proper
authentication and authorization controls.
"""

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
    """ViewSet for Execution model operations.

    This ViewSet provides REST API endpoints for managing execution
    records with proper filtering, searching, and ordering capabilities.
    It enforces authentication and project-based authorization, and
    provides report download functionality for completed executions.

    Attributes:
        queryset: QuerySet for Execution model instances.
        serializer_class: Serializer class for Execution model.
        filterset_class: Filter class for query filtering.
        permission_classes: List of permission classes for access control.
        search_fields: Fields available for text search.
        ordering_fields: Fields available for result ordering.
        http_method_names: Allowed HTTP methods for this ViewSet.
    """

    queryset = Execution.objects.all()
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
        """Download execution report file.

        This action allows users to download the output report file
        for a completed execution. Only completed executions can
        have downloadable reports.

        Args:
            request: The HTTP request object.
            pk: The primary key of the execution.

        Returns:
            FileResponse: The report file as a downloadable response,
                or an error response if the execution is not completed
                or the file doesn't exist.
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
