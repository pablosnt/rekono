"""Django REST framework views for security report generation and management.

Provides REST API endpoints for report lifecycle management including creation,
status tracking, and file download with multi-format support and background
processing capabilities.
"""

import importlib
import json
import threading
import uuid
from typing import Any, cast
from xml.etree import ElementTree as ET

from django.db.models import Q, QuerySet
from django.forms.models import model_to_dict
from django.http import FileResponse
from django.template.loader import get_template
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from xhtml2pdf import pisa

from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import OSINT, Credential, Exploit, Host, Port, Technology, Vulnerability
from framework.views import BaseViewSet
from platforms.email.notifications import SMTP
from platforms.telegram_app.notifications import Telegram
from projects.models import Project
from rekono.settings import CONFIG, STATIC_URL, STATICFILES_DIRS
from reporting.enums import FindingName, ReportFormat, ReportStatus
from reporting.filters import ReportFilter
from reporting.models import Report
from reporting.serializers import CreateReportSerializer, ReportSerializer
from security.authorization.permissions import OwnerPermission, RekonoModelPermission
from targets.models import Target
from tasks.models import Task


class ReportingViewSet(BaseViewSet):
    """ViewSet for security report generation and management.

    Provides REST API endpoints for report operations including creation with
    background processing, status tracking, and secure file download. Supports
    multiple output formats with advanced filtering and notification capabilities.

    Custom Actions:
        download: Download generated report files with secure access controls

    Attributes:
        queryset (QuerySet): Report model instances
        serializer_class (Serializer): Default serializer for report operations
        filterset_class (FilterSet): Filter class for report queries
        permission_classes (list): Required permissions including ownership validation
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods (GET, POST, DELETE)
        owner_field (str): Field used for ownership-based access control
    """

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_class = ReportFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = ["format", "status"]
    ordering_fields = ["id", "project", "target", "task", "status", "format", "user", "date"]
    http_method_names = ["get", "post", "delete"]
    owner_field = "user"

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        """Extract project from request data based on scope hierarchy.

        Args:
            project_field (str): The project field name (unused in current implementation)
            data (dict[str, Any]): Request data containing scope information

        Returns:
            Project | None: The associated project or None if not found
        """
        return (
            cast(Task, data.get("task")).target.project
            if data.get("task")
            else (cast(Target, data.get("target")).project if data.get("target") else data.get("project"))
        )

    def get_queryset(self) -> QuerySet:
        """Get filtered queryset based on user project membership.

        Returns:
            QuerySet: Reports filtered to only include those accessible by the current user
        """
        return (
            (
                super()
                .get_queryset()
                .filter(
                    Q(project__members=self.request.user)
                    | Q(target__project__members=self.request.user)
                    | Q(task__target__project__members=self.request.user)
                )
            )
            if self.request.user.id
            else QuerySet.none()
        )

    def get_serializer_class(self) -> Serializer:
        """Get appropriate serializer class based on request method.

        Returns:
            Serializer: CreateReportSerializer for POST requests, ReportSerializer otherwise
        """
        return CreateReportSerializer if self.request.method == "POST" else super().get_serializer_class()

    @extend_schema(request=CreateReportSerializer, responses=ReportSerializer)
    def create(self, request: Request, *args: Any, **kwargs: Any):
        """Create a new report with background generation processing.

        Validates report parameters, processes findings data, and initiates
        background report generation with status tracking.

        Args:
            request (Request): HTTP request containing report configuration
            *args (Any): Additional positional arguments
            **kwargs (Any): Additional keyword arguments

        Returns:
            Response: HTTP 201 with report instance or HTTP 404 if no findings found
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        findings: tuple[dict[int, Any], dict[int, list[int]], list[int]] | dict[type[Finding], list[Finding]] = {}
        if serializer.validated_data["format"] == ReportFormat.PDF:
            findings, count = self._get_findings_for_pdf_report(serializer)
        else:
            findings, count = self._get_json_findings_by_type(serializer)
        if count == 0:
            return Response({"findings": "No findings found with this criterion"}, status=status.HTTP_404_NOT_FOUND)
        self.perform_create(serializer)
        threading.Thread(target=self._create_report_file, args=(serializer.instance, findings)).start()
        return Response(self.get_serializer(instance=serializer.instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request: Request, pk: str, *args: Any, **kwargs: Any) -> Response:
        """Delete report and associated file from storage.

        Args:
            request (Request): HTTP request object
            pk (str): Primary key of the report to remove
            *args (Any): Additional positional arguments
            **kwargs (Any): Additional keyword arguments

        Returns:
            Response: Standard deletion response
        """
        report = self.get_object()
        path = (CONFIG.generated_reports / report.path) if report.path else None
        if path and path.exists():
            path.unlink()
        return super().destroy(request, *args, **kwargs)

    @extend_schema(request=None, responses={200: OpenApiResponse(description="Generated report file"), 404: None})
    @action(detail=True, methods=["GET"])
    def download(self, request: Request, pk: str) -> FileResponse:
        """Download generated report file with secure access validation.

        Args:
            request (Request): HTTP request object
            pk (str): Primary key of the report to download

        Returns:
            FileResponse: Report file download or error response for invalid status/missing file
        """
        report = self.get_object()
        if report.status != ReportStatus.READY:
            messages = {
                ReportStatus.PENDING: "Report is not available yet",
                ReportStatus.ERROR: "Report generation failed",
            }
            return Response({"report": messages[report.status]}, status=status.HTTP_400_BAD_REQUEST)
        path = CONFIG.generated_reports / (report.path or "")
        if not report.path or not path.is_file():
            return Response(status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            path.open("rb"),
            as_attachment=True,
            filename=f"{str(uuid.uuid4())}.{report.format.lower()}",
            status=status.HTTP_200_OK,
        )

    def _get_json_findings_by_type(
        self, serializer: ReportSerializer
    ) -> tuple[dict[type[Finding], list[dict[str, Any]]], int]:
        """Extract findings data organized by type for JSON/XML report generation.

        Args:
            serializer (ReportSerializer): Validated report serializer with filtering criteria

        Returns:
            tuple[dict[type[Finding], list[dict[str, Any]]], int]: Findings by type and total count
        """
        findings = {}
        count = 0
        models = importlib.import_module("findings.models")
        for finding_type in serializer.validated_finding_types:
            model = getattr(models, finding_type)
            query_filter = (
                {**serializer.validated_filter, **serializer.validated_triage_filter}
                if hasattr(model, "triage_status")
                else serializer.validated_filter
            )
            query = model.objects.filter(**query_filter).all()
            if model == Vulnerability:
                query = query.order_by("-severity")
            findings[model.__name__.lower()] = [
                {k: v for k, v in model_to_dict(f).items() if k != "executions"} for f in query
            ]
            count += query.count()
        return findings, count

    def _get_findings_for_pdf_report(self, serializer: ReportSerializer) -> tuple[dict[str, Any], int]:
        """Extract hierarchical findings data with statistics for PDF report generation.

        Args:
            serializer (ReportSerializer): Validated report serializer with filtering criteria

        Returns:
            tuple[dict[str, Any], int]: Hierarchical findings with statistics and total count
        """
        count = 0
        results = {"findings": {}, "stats": {severity.name.lower(): 0 for severity in Severity}, "stats_by_target": {}}
        for target in (
            [serializer.validated_data.get("task").target]
            if serializer.validated_data.get("task")
            else (
                [serializer.validated_data.get("target")]
                if serializer.validated_data.get("target")
                else serializer.validated_data.get("project").targets.all()
            )
        ):
            scope_filter = (
                {"executions__task": serializer.validated_data.get("task")}
                if serializer.validated_data.get("task")
                else {"executions__task__target": target}
            )
            results["stats_by_target"][target.id] = {severity.name.lower(): 0 for severity in Severity}
            _osint = OSINT.objects.filter(
                **{**scope_filter, **serializer.validated_filter, **serializer.validated_triage_filter}
            )
            _target_count = _osint.count()
            _findings = {FindingName.OSINT.value: _osint.all(), FindingName.HOST.value: []}
            for host in Host.objects.filter(**{**scope_filter, **serializer.validated_filter}).all():
                _ports = Port.objects.filter(**{**scope_filter, "host": host, **serializer.validated_filter})
                _technologies = Technology.objects.filter(
                    **{**scope_filter, "port__host": host, **serializer.validated_filter}
                )
                _credentials = Credential.objects.filter(
                    **{
                        **scope_filter,
                        "technology__port__host": host,
                        **serializer.validated_filter,
                        **serializer.validated_triage_filter,
                    }
                )
                _vulnerabilities = (
                    Vulnerability.objects.filter(
                        **{**scope_filter, **serializer.validated_filter, **serializer.validated_triage_filter}
                    )
                    .filter(Q(technology__port__host=host) | Q(port__host=host))
                    .order_by("-severity")
                )
                _exploits = Exploit.objects.filter(
                    **{**scope_filter, **serializer.validated_filter, **serializer.validated_triage_filter}
                ).filter(
                    Q(technology__port__host=host)
                    | Q(vulnerability__technology__port__host=host)
                    | Q(vulnerability__port__host=host)
                )
                _target_count += (
                    1  # The host finding counts
                    + _ports.count()
                    + _technologies.count()
                    + _credentials.count()
                    + _vulnerabilities.count()
                    + _exploits.count()
                )
                _findings[FindingName.HOST.value].append(
                    {
                        FindingName.HOST.value: host,
                        FindingName.PORT.value: _ports.all(),
                        FindingName.TECHNOLOGY.value: _technologies.all(),
                        FindingName.CREDENTIAL.value: _credentials.all(),
                        FindingName.VULNERABILITY.value: _vulnerabilities.all(),
                        FindingName.EXPLOIT.value: _exploits.all(),
                    }
                )
                for vulnerability in _vulnerabilities.all():
                    _severity = Severity(vulnerability.severity).name.lower()
                    results["stats_by_target"][target.id][_severity] += 1
                    results["stats"][_severity] += 1
                for credential in _credentials.all():
                    _severity = (Severity.HIGH if credential.secret else Severity.LOW).name.lower()
                    results["stats_by_target"][target.id][_severity] += 1
                    results["stats"][_severity] += 1
            if _target_count > 0:
                results["findings"][target.id] = _findings
                count += _target_count
            else:
                results["stats_by_target"].pop(target.id)
        return results, count

    def _create_report_file(self, report: Report, *findings: Any) -> None:
        """Generate report file in background thread with status updates.

        Args:
            report (Report): Report instance to generate file for
            *findings (Any): Findings data for report content
        """
        filename = f"{str(uuid.uuid4())}.{report.format.lower()}"
        success = getattr(self, f"_create_{report.format.lower()}_report")(filename, report, *findings)
        if success:
            report.path = filename
            report.status = ReportStatus.READY
            report.save(update_fields=["path", "status"])
            Telegram().report_created(report)
            SMTP().report_created(report)
        else:
            report.status = ReportStatus.ERROR
            report.save(update_fields=["status"])

    def _create_json_report(
        self, filename: str, report: Report, findings: dict[type[Finding], list[dict[str, Any]]]
    ) -> bool:
        """Generate JSON format report file.

        Args:
            filename (str): Target filename for the report
            report (Report): Report instance for context
            findings (dict[type[Finding], list[dict[str, Any]]]): Findings data to serialize

        Returns:
            bool: True if generation succeeded, False on error
        """
        try:
            with (CONFIG.generated_reports / filename).open("w") as report:
                json.dump(findings, report, ensure_ascii=True, indent=4)
            return True
        except Exception:
            return False

    def _dict_to_xml(self, element: ET.Element, data: dict[str, Any]) -> ET.Element:
        """Recursively convert dictionary data to XML elements.

        Args:
            element (ET.Element): Parent XML element to append children to
            data (dict[str, Any]): Dictionary data to convert

        Returns:
            ET.Element: XML element with converted data as children
        """
        for key, value in data.items():
            child = ET.Element(key)
            if isinstance(value, dict):
                element.append(self._dict_to_xml(child, value))
            else:
                child.text = str(value or "")
                element.append(child)
        return element

    def _create_xml_report(
        self, filename: str, report: Report, findings: dict[type[Finding], list[dict[str, Any]]]
    ) -> bool:
        """Generate XML format report file.

        Args:
            filename (str): Target filename for the report
            report (Report): Report instance for context
            findings (dict[type[Finding], list[dict[str, Any]]]): Findings data to serialize

        Returns:
            bool: True if generation succeeded, False on error
        """
        root = ET.Element("findings")
        for finding_type, finding_list in findings.items():
            for finding in finding_list:
                root.append(self._dict_to_xml(ET.Element(finding_type.lower()), finding))
        ET.indent(root, space="\t")
        with (CONFIG.generated_reports / filename).open("w") as report:
            report.write(ET.tostring(root, encoding="unicode"))
        return True

    def _pdf_static_content(self, uri: str, rel: str) -> str:
        """Resolve static file paths for PDF generation.

        Callback function for xhtml2pdf to convert relative URIs to absolute paths
        for CSS and image resources during PDF generation.

        Args:
            uri (str): Relative URI from HTML template
            rel (str): Relationship type (unused)

        Returns:
            str: Absolute file path or original URI if not found
        """
        # Callback function for PDF generation to resolve static file paths
        # Converts relative URIs to absolute paths so xhtml2pdf can access CSS/images
        if f"/{STATIC_URL}" in uri:
            filepath = uri.split(f"/{STATIC_URL}", 1)[1]
            for parent in [STATICFILES_DIRS[0], CONFIG.home]:
                location = parent / filepath
                if location.exists():
                    return str(location)
        return uri

    def _create_pdf_report(self, filename: str, report: Report, findings: dict[str, Any]) -> bool:
        """Generate PDF format report file with template rendering.

        Args:
            filename (str): Target filename for the report
            report (Report): Report instance for context
            findings (dict[str, Any]): Hierarchical findings data with statistics

        Returns:
            bool: True if generation succeeded, False on PDF creation errors
        """
        scope = report.task or report.target or report.project
        template = get_template(CONFIG.pdf_report_template).render(
            {
                "project": scope.parent_project,
                "targets": [scope.target]
                if isinstance(scope, Task)
                else ([scope] if isinstance(scope, Target) else (scope.targets.all() if not CONFIG.testing else [])),
                "findings": findings["findings"],
                "stats_by_target": findings["stats_by_target"],
                "stats": findings["stats"],
            }
        )
        with (CONFIG.generated_reports / filename).open("wb") as report:
            # TOTEST
            pisa_status = pisa.CreatePDF(template, dest=report, link_callback=self._pdf_static_content)
        return not pisa_status.err
