"""Django REST framework views for execution models.

Provides REST API views for execution records including list, retrieve
operations and report download functionality with proper security controls.
"""

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
    """ViewSet for Execution model operations.

    Provides REST API endpoints for execution records with filtering, searching,
    and ordering capabilities. Includes report download functionality for
    completed executions.

    Custom Actions:
        download_report: Download execution output files for completed executions

    Attributes:
        queryset (QuerySet): Execution model instances
        serializer_class (Serializer): Serializer for Execution model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods (GET only)
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
        """Download execution report file.

        Allows downloading output report files for completed executions.
        Only executions with COMPLETED status can have downloadable reports.

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the execution

        Returns:
            FileResponse: Report file download or error response
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
