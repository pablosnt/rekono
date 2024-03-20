# Create your views here.

import importlib
import json
import threading
import uuid
from typing import Any, Dict, List, Optional, Tuple, Type, cast
from xml.etree import ElementTree as ET  # nosec

from django.db.models import Q, QuerySet
from django.forms.models import model_to_dict
from django.http import FileResponse
from django.template.loader import get_template
from drf_spectacular.utils import OpenApiResponse, extend_schema
from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Port,
    Technology,
    Vulnerability,
)
from framework.views import BaseViewSet
from platforms.mail.notifications import SMTP
from platforms.telegram_app.notifications.notifications import Telegram
from projects.models import Project
from rekono.settings import CONFIG, STATIC_URL, STATICFILES_DIRS
from reporting.enums import FindingName, ReportFormat, ReportStatus
from reporting.filters import ReportFilter
from reporting.models import Report
from reporting.serializers import CreateReportSerializer, ReportSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from security.authorization.permissions import OwnerPermission, RekonoModelPermission
from targets.models import Target
from tasks.models import Task
from xhtml2pdf import pisa


class ReportingViewSet(BaseViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_class = ReportFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    ordering_fields = [
        "id",
        "project",
        "target",
        "task",
        "status",
        "format",
        "user",
        "date",
    ]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]
    owner_field = "user"

    def _get_project_from_data(
        self, project_field: str, data: Dict[str, Any]
    ) -> Optional[Project]:
        return (
            cast(Task, data.get("task")).target.project
            if data.get("task")
            else (
                cast(Target, data.get("target")).project
                if data.get("target")
                else data.get("project")
            )
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
            else None
        )

    def get_serializer_class(self) -> Serializer:
        return (
            CreateReportSerializer
            if self.request.method == "POST"
            else super().get_serializer_class()
        )

    @extend_schema(request=CreateReportSerializer, responses=ReportSerializer)
    def create(self, request: Request, *args: Any, **kwargs: Any):
        serializer = self.get_serializer_class()(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        findings = (
            self._get_findings_to_pdf_report(serializer)
            if serializer.validated_data["format"] == ReportFormat.PDF
            else self._get_findings_to_report(serializer)
        )
        if (isinstance(findings, list) and not findings) or (
            isinstance(findings, tuple) and not findings[0]
        ):
            return Response(
                {"findings": "No findings found with this criteria"},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.perform_create(serializer)
        threading.Thread(
            target=self._create_report_file,
            args=(serializer.instance,)
            + (
                (findings[0], findings[1], findings[2])
                if isinstance(findings, tuple)
                else (findings,)
            ),
        ).start()
        return Response(
            ReportSerializer(serializer.instance).data, status=status.HTTP_201_CREATED
        )

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        report = self.get_object()
        path = (CONFIG.generated_reports / report.path) if report.path else None
        if path and path.exists():
            path.unlink()
        super().destroy(request, *args, **kwargs)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description="Generated report file"),
            404: None,
        },
    )
    @action(detail=True, methods=["GET"], url_path="download", url_name="download")
    def download(self, request: Request, pk: str) -> FileResponse:
        report = self.get_object()
        if report.status != ReportStatus.READY:
            messages = {
                ReportStatus.PENDING: "Report is not available yet",
                ReportStatus.ERROR: "Report generation failed",
            }
            return Response(
                {"report": messages[report.status]}, status=status.HTTP_400_BAD_REQUEST
            )
        path = CONFIG.generated_reports / (report.path or "")
        if not report.path or not path.is_file():
            return Response(status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            path.open("rb"),
            as_attachment=True,
            filename=f"{str(uuid.uuid4())}.{report.format.lower()}",
            status=status.HTTP_200_OK,
        )

    def _get_findings_to_report(
        self, serializer: ReportSerializer
    ) -> Dict[Type[Finding], List[Finding]]:
        findings = {}
        models = importlib.import_module("findings.models")
        for finding_type in serializer.validated_finding_types:
            model = getattr(models, finding_type)
            query = model.objects.filter(**serializer.validated_filter).all()
            if model == Vulnerability:
                query = query.order_by("severity")
            findings[model.__name__.lower()] = [
                {k: v for k, v in model_to_dict(f).items() if k != "executions"}
                for f in query
            ]
        return findings

    def _get_findings_to_pdf_report(
        self, serializer: ReportSerializer
    ) -> Tuple[Dict[int, Any], Dict[int, List[int]], List[int]]:
        label_index = [s.value for s in reversed(Severity)]
        stats = [0] * len(Severity)
        stats_by_target = {}
        findings_by_target = {}
        filter = serializer.validated_filter
        for target in (
            serializer.validated_data.get("project").targets.all()
            if serializer.validated_data.get("project")
            else [
                serializer.validated_data.get("target")
                or serializer.validated_data.get("task").target
            ]
        ):
            filter["executions__task__target"] = target
            stats_by_target[target.id] = [0] * len(Severity)
            findings_by_target[target.id] = {
                FindingName.OSINT.value: OSINT.objects.filter(**filter).all(),
                FindingName.HOST.value: [
                    {
                        FindingName.HOST.value: host,
                        FindingName.PORT.value: Port.objects.filter(
                            host=host, **filter
                        ).all(),
                        FindingName.TECHNOLOGY.value: Technology.objects.filter(
                            port__host=host, **filter
                        ).all(),
                        FindingName.CREDENTIAL.value: Credential.objects.filter(
                            technology__port__host=host, **filter
                        ).all(),
                        FindingName.VULNERABILITY.value: Vulnerability.objects.filter(
                            **filter
                        )
                        .filter(Q(technology__port__host=host) | Q(port__host=host))
                        .order_by("severity")
                        .all(),
                        FindingName.EXPLOIT.value: Exploit.objects.filter(**filter)
                        .filter(
                            Q(technology__port__host=host)
                            | Q(vulnerability__technology__port__host=host)
                            | Q(vulnerability__port__host=host)
                        )
                        .all(),
                    }
                    for host in Host.objects.filter(**filter)
                ],
            }
            if (
                len(findings_by_target[target.id][FindingName.OSINT.value]) == 0
                and len(findings_by_target[target.id][FindingName.HOST.value]) == 0
            ):
                findings_by_target.pop(target.id)
            else:
                for host in findings_by_target[target.id][FindingName.HOST.value]:
                    for vulnerability in host[FindingName.VULNERABILITY.value]:
                        index = label_index.index(vulnerability.severity)
                        stats[index] += 1
                        stats_by_target[target.id][index] += 1
                    for credential in host[FindingName.CREDENTIAL.value]:
                        index = label_index.index(Severity.HIGH.value if credential.secret else Severity.LOW.value)
                        stats[index] += 1
                        stats_by_target[target.id][index] += 1
        return findings_by_target, stats_by_target, stats

    def _create_report_file(self, report: Report, *findings: Any) -> None:
        filename = f"{str(uuid.uuid4())}.{report.format.lower()}"
        success = getattr(self, f"_{report.format.lower()}_report")(
            filename, report, *findings
        )
        if success:
            report.path = filename
            report.status = ReportStatus.READY
            report.save(update_fields=["path", "status"])
            Telegram().report_created(report)
            SMTP().report_created(report)
        else:
            report.status = ReportStatus.ERROR
            report.save(update_fields=["status"])

    def _json_report(
        self,
        filename: str,
        report: Report,
        findings: Dict[Type[Finding], List[Finding]],
    ) -> None:
        with (CONFIG.generated_reports / filename).open("w") as filepath:
            json.dump(findings, filepath, ensure_ascii=True, indent=4)
        return True

    def _dict_to_xml(self, element: ET.Element, data: Dict[str, Any]) -> ET.Element:
        for key, value in data.items():
            child = ET.Element(key)
            if isinstance(value, dict):
                element.append(self._dict_to_xml(child, value))
            else:
                child.text = str(value or "")
                element.append(child)
        return element

    def _xml_report(
        self,
        filename: str,
        report: Report,
        findings: Dict[Type[Finding], List[Finding]],
    ) -> None:
        root = ET.Element("findings")
        for finding_type, finding_list in findings.items():
            for finding in finding_list:
                root.append(
                    self._dict_to_xml(ET.Element(finding_type.lower()), finding)
                )
        ET.indent(root, space="\t")
        with (CONFIG.generated_reports / filename).open("w") as filepath:
            filepath.write(ET.tostring(root, encoding="unicode"))
        return True

    def _pdf_static_content(self, uri: str, rel: str) -> str:
        if f"/{STATIC_URL}" in uri:
            filepath = uri.split(f"/{STATIC_URL}", 1)[1]
            for parent in [STATICFILES_DIRS[0], CONFIG.home]:
                location = parent / filepath
                if location.exists():
                    return str(location)
        return uri

    def _pdf_report(
        self,
        filename: str,
        report: Report,
        findings_by_target: Dict[int, Any],
        stats_by_target: Dict[int, List[int]],
        stats: List[int],
    ) -> None:
        template = get_template(CONFIG.pdf_report_template).render(
            {
                "project": report.project
                or (
                    report.target.project
                    if report.target
                    else report.task.target.project
                ),
                "targets": report.project.targets.all()
                if report.project
                else [report.target or report.task.target],
                "findings": findings_by_target,
                "stats_by_target": stats_by_target,
                "stats": stats,
            }
        )
        with (CONFIG.generated_reports / filename).open("wb") as filepath:
            pisa_status = pisa.CreatePDF(
                template, dest=filepath, link_callback=self._pdf_static_content
            )
        return not pisa_status.err
