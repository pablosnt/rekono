"""Viewset of the report endpoints.

The findings are queried when the report is requested, so the response can tell the
user right away if there is nothing to report, and the file is written in a thread
so a big report doesn't block the request.
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
    """Request, download, and remove the reports of the findings.

    Attributes:
        queryset: All the reports, filtered later by project membership.
        serializer_class: Serializer of the reports.
        filterset_class: Filters of the reports.
        permission_classes: Role permissions plus the ownership of the report, so
          only the user that requested it can download or remove it.
        search_fields: Free text search over the format and the status.
        ordering_fields: Fields that the reports can be sorted by.
        http_method_names: A report can't be updated, only requested, downloaded,
          and removed.
        owner_field: Field with the user that requested the report.
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
        """Get the project of the scope that the new report covers.

        Args:
            project_field: Not used, since the project of a report comes from its
              scope instead of from a field of the request.
            data: Data of the report that is being created.

        Returns:
            The project that the report will belong to, taken from the most
            specific scope that the request provides, or None if it provides no
            scope at all.
        """
        return (
            cast(Task, data.get("task")).target.project
            if data.get("task")
            else (cast(Target, data.get("target")).project if data.get("target") else data.get("project"))
        )

    def get_queryset(self) -> QuerySet:
        """Get the reports of the projects that the user belongs to.

        Returns:
            The reports that the user can access, whether they are scoped to a
            project, a target, or a task. None for an unauthenticated request.
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
        """Get the serializer that accepts the report options for the creation.

        Returns:
            The creation serializer for POST, which accepts the scope and the
            format, and the standard one for the rest of the methods.
        """
        return CreateReportSerializer if self.request.method == "POST" else super().get_serializer_class()

    @extend_schema(request=CreateReportSerializer, responses=ReportSerializer)
    def create(self, request: Request, *args: Any, **kwargs: Any):
        """Request a new report and start generating its file in the background.

        Args:
            request: Request with the scope, the format, and the criteria that
              select the findings.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            The created report, which is still pending until its file is written,
            or a not found error if no finding matches the requested criteria.
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
        """Remove a report and the file that was generated for it.

        Args:
            request: Request that asks for the report to be removed.
            pk: Identifier of the report, taken from the URL.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            An empty response, or a validation error if the report is still being
            generated, since the thread that writes the file would keep running
            against a report that doesn't exist anymore and leave the file behind.
        """
        report = self.get_object()
        if report.status == ReportStatus.PENDING:
            return Response(
                {"report": "Report can't be deleted while it is being generated"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        path = (CONFIG.generated_reports / report.path) if report.path else None
        if path and path.exists():
            path.unlink()
        return super().destroy(request, *args, **kwargs)

    @extend_schema(request=None, responses={200: OpenApiResponse(description="Generated report file"), 404: None})
    @action(detail=True, methods=["GET"])
    def download(self, request: Request, pk: str) -> FileResponse:
        """Download the file that was generated for a report.

        Args:
            request: Request that asks for the file.
            pk: Identifier of the report, taken from the URL.

        Returns:
            The report file, a validation error if the report isn't ready yet or
            its generation failed, or a not found error if the file is gone.
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
        """Get the findings of the report grouped by their type.

        Args:
            serializer: Validated report serializer, whose filters select the
              findings to include.

        Returns:
            The findings of each requested type, already sorted by what matters in
            each one, and how many findings the report will include in total.
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
            query = model.objects.filter(**query_filter).distinct()
            if model == Vulnerability:
                query = query.order_by("-severity")
            elif model == Port:
                query = query.order_by("port")
            elif model == OSINT:
                query = query.order_by("data")
            findings[model.__name__.lower()] = [
                {k: v for k, v in model_to_dict(f).items() if k != "executions"} for f in query
            ]
            count += query.count()
        return findings, count

    def _get_findings_for_pdf_report(self, serializer: ReportSerializer) -> tuple[dict[str, Any], int]:
        """Get the findings of the report grouped by target and by host.

        Args:
            serializer: Validated report serializer, whose filters select the
              findings to include.

        Returns:
            The findings of each host of each target, with the number of findings
            per severity that the charts of the document need, and how many
            findings the report will include in total. The targets without
            findings are left out, so the document has no empty sections.
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
            _osint = (
                OSINT.objects.filter(
                    **{**scope_filter, **serializer.validated_filter, **serializer.validated_triage_filter}
                )
                .order_by("data")
                .distinct()
            )
            _target_count = _osint.count()
            _findings = {FindingName.OSINT.value: _osint.all(), FindingName.HOST.value: []}
            for host in Host.objects.filter(**{**scope_filter, **serializer.validated_filter}).distinct():
                _ports = (
                    Port.objects.filter(**{**scope_filter, "host": host, **serializer.validated_filter})
                    .order_by("port")
                    .distinct()
                )
                _technologies = Technology.objects.filter(
                    **{**scope_filter, "port__host": host, **serializer.validated_filter}
                ).distinct()
                _credentials = Credential.objects.filter(
                    **{
                        **scope_filter,
                        "technology__port__host": host,
                        **serializer.validated_filter,
                        **serializer.validated_triage_filter,
                    }
                ).distinct()
                _vulnerabilities = (
                    Vulnerability.objects.filter(
                        **{**scope_filter, **serializer.validated_filter, **serializer.validated_triage_filter}
                    )
                    .filter(Q(technology__port__host=host) | Q(port__host=host))
                    .order_by("-severity")
                    .distinct()
                )
                _exploits = (
                    Exploit.objects.filter(
                        **{**scope_filter, **serializer.validated_filter, **serializer.validated_triage_filter}
                    )
                    .filter(
                        Q(technology__port__host=host)
                        | Q(vulnerability__technology__port__host=host)
                        | Q(vulnerability__port__host=host)
                    )
                    .distinct()
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
                # The credentials have no severity of their own, so an exposed secret is
                # counted as a high risk and a leaked user name as a low one
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
        """Generate the file of a report and notify the user that it's ready.

        Args:
            report: Report whose file must be generated.
            *findings: Findings to include, in the shape that the format needs.
        """
        filename = f"{str(uuid.uuid4())}.{report.format.lower()}"
        try:
            success = getattr(self, f"_create_{report.format.lower()}_report")(filename, report, *findings)
        except Exception as ex:
            self.logger.error(f"Error while generating the {report.format} report {report.id}: {str(ex)}")
            success = False
        # This runs in a raw thread instead of in a queue, so nothing else would ever move the
        # report out of the pending status if the generation fails
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
        """Write the findings of a report as a JSON file.

        Args:
            filename: Name of the file to write inside the generated reports
              directory.
            report: Report whose scope and format are being generated.
            findings: Findings to include, as the corresponding _get_findings method
              returned them.

        Returns:
            Whether the file could be written.
        """
        try:
            with (CONFIG.generated_reports / filename).open("w") as report:
                json.dump(findings, report, ensure_ascii=True, indent=4, default=str)
            return True
        except Exception:
            return False

    def _dict_to_xml(self, element: ET.Element, data: dict[str, Any]) -> ET.Element:
        """Add the data of a finding to an XML element, as one child per field.

        Args:
            element: Element that the fields are added to, modified in place.
            data: Finding fields, whose nested dictionaries become nested
              elements.

        Returns:
            The same element, so the recursive calls can append it directly.
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
        """Write the findings of a report as an XML file.

        Args:
            filename: Name of the file to write inside the generated reports
              directory.
            report: Report whose scope and format are being generated.
            findings: Findings to include, as _get_json_findings_by_type returned
              them.

        Returns:
            Always true, since any failure raises instead of being reported.
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
        """Get the location of a static file referenced by the PDF template.

        Args:
            uri: Reference to the file, as the template writes it.
            rel: Not used, accepted for compatibility with the xhtml2pdf callback.

        Returns:
            The path of the file in the file system, or the reference itself if the
            file isn't there, since xhtml2pdf just skips what it can't resolve.
        """
        if f"/{STATIC_URL}" in uri:
            filepath = uri.split(f"/{STATIC_URL}", 1)[1]
            for parent in [STATICFILES_DIRS[0], CONFIG.home]:
                location = parent / filepath
                if location.exists():
                    return str(location)
        return uri

    def _create_pdf_report(self, filename: str, report: Report, findings: dict[str, Any]) -> bool:
        """Write the findings of a report as a PDF document.

        Args:
            filename: Name of the file to write inside the generated reports
              directory.
            report: Report whose scope and format are being generated.
            findings: Findings to include, as the corresponding _get_findings method
              returned them.

        Returns:
            Whether the document could be created.
        """
        scope = report.task or report.target or report.project
        template = get_template(CONFIG.pdf_report_template).render(
            {
                "project": scope.parent_project,
                "targets": [scope.target]
                if isinstance(scope, Task)
                # This method runs in a background thread, and the test database is an in-memory SQLite
                # instance scoped per connection, so a fresh query here would see an empty database. The
                # task/target branches above reuse objects already loaded on the calling thread, avoiding
                # the issue, but a project-scope report needs a live query, so it is skipped during tests.
                else ([scope] if isinstance(scope, Target) else (scope.targets.all() if not CONFIG.testing else [])),
                "findings": findings["findings"],
                "stats_by_target": findings["stats_by_target"],
                "stats": findings["stats"],
            }
        )
        with (CONFIG.generated_reports / filename).open("wb") as report:
            pisa_status = pisa.CreatePDF(template, dest=report, link_callback=self._pdf_static_content)
        return not pisa_status.err
