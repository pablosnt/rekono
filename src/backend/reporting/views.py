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
from platforms.mail.notifications import SMTP
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
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_class = ReportFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = ["format", "status"]
    ordering_fields = ["id", "project", "target", "task", "status", "format", "user", "date"]
    http_method_names = ["get", "post", "delete"]
    owner_field = "user"

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        return (
            cast(Task, data.get("task")).target.project
            if data.get("task")
            else (cast(Target, data.get("target")).project if data.get("target") else data.get("project"))
        )

    def get_queryset(self) -> QuerySet:
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
        return CreateReportSerializer if self.request.method == "POST" else super().get_serializer_class()

    @extend_schema(request=CreateReportSerializer, responses=ReportSerializer)
    def create(self, request: Request, *args: Any, **kwargs: Any):
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

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        report = self.get_object_or_404()
        path = (CONFIG.generated_reports / report.path) if report.path else None
        if path and path.exists():
            path.unlink()
        return super().destroy(request, *args, **kwargs)

    @extend_schema(request=None, responses={200: OpenApiResponse(description="Generated report file"), 404: None})
    @action(detail=True, methods=["GET"])
    def download(self, request: Request, pk: str) -> FileResponse:
        report = self.get_object_or_404()
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
        count = 0
        results = {"findings": {}, "stats": {severity.name.upper(): 0 for severity in Severity}, "stats_by_target": {}}
        for target in (
            [serializer.validated_data.get("task").target]
            if serializer.validated_data.get("task")
            else (
                [serializer.validated_data.get("target")]
                if serializer.validated_data.get("target")
                else serializer.validated_data.get("project").targets.all()
            )
        ):
            target_filter = {"executions__task__target": target}
            results["stats_by_target"][target.id] = {severity.name.upper(): 0 for severity in Severity}
            _osint = OSINT.objects.filter(
                **{**target_filter, **serializer.validated_filter, **serializer.validated_triage_filter}
            )
            _target_count = _osint.count()
            _findings = {FindingName.OSINT.value: _osint.all(), FindingName.HOST.value: []}
            for host in Host.objects.filter(**{**target_filter, **serializer.validated_filter}).all():
                _ports = Port.objects.filter(**{**target_filter, "host": host, **serializer.validated_filter})
                _technologies = Technology.objects.filter(
                    **{**target_filter, "port__host": host, **serializer.validated_filter}
                )
                _credentials = Credential.objects.filter(
                    **{
                        **target_filter,
                        "technology__port__host": host,
                        **serializer.validated_filter,
                        **serializer.validated_triage_filter,
                    }
                )
                _vulnerabilities = (
                    Vulnerability.objects.filter(
                        **{
                            **target_filter,
                            **serializer.validated_filter,
                            **serializer.validated_triage_filter,
                        }
                    )
                    .filter(Q(technology__port__host=host) | Q(port__host=host))
                    .order_by("-severity")
                )
                _exploits = Exploit.objects.filter(
                    **{
                        **target_filter,
                        **serializer.validated_filter,
                        **serializer.validated_triage_filter,
                    }
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
                    _severity = vulnerability.severity.name.upper()
                    results["stats_by_target"][target.id][_severity] += 1
                    results["stats"][_severity] += 1
                for credential in _credentials.all():
                    _severity = (Severity.HIGH if credential.secret else Severity.LOW).name.upper()
                    results["stats_by_target"][target.id][_severity] += 1
                    results["stats"][_severity] += 1
            if _target_count > 0:
                results["findings"][target.id] = _findings
                count += _target_count
            else:
                results["stats_by_target"].pop(target.id)
        return results, count

    def _create_report_file(self, report: Report, *findings: Any) -> None:
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
        try:
            with (CONFIG.generated_reports / filename).open("w") as report:
                json.dump(findings, report, ensure_ascii=True, indent=4)
            return True
        except Exception:
            return False

    def _dict_to_xml(self, element: ET.Element, data: dict[str, Any]) -> ET.Element:
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
        root = ET.Element("findings")
        for finding_type, finding_list in findings.items():
            for finding in finding_list:
                root.append(self._dict_to_xml(ET.Element(finding_type.lower()), finding))
        ET.indent(root, space="\t")
        with (CONFIG.generated_reports / filename).open("w") as report:
            report.write(ET.tostring(root, encoding="unicode"))
        return True

    def _pdf_static_content(self, uri: str, rel: str) -> str:
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
            pisa_status = pisa.CreatePDF(template, dest=report, link_callback=self._pdf_static_content)
        return not pisa_status.err
