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
from drf_spectacular.utils import OpenApiResponse, extend_schema
from findings.framework.models import Finding
from framework.views import BaseViewSet
from platforms.mail.notifications import SMTP
from platforms.telegram_app.notifications.notifications import Telegram
from projects.models import Project
from rekono.settings import CONFIG
from reporting.enums import FindingName, ReportStatus
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
        report, serializer = self._create_report(request)
        findings = self._get_findings_to_report(serializer)
        threading.Thread(
            target=getattr(self, f"_{report.format.lower()}_report"),
            args=(report, findings),
        ).start()
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        report = self.get_object()
        if report.path:
            (CONFIG.generated_reports / report.path).unlink()
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
        if report.status != ReportStatus.CREATED:
            return Response(
                {"report": "Report is not available yet"},
                status=status.HTTP_400_BAD_REQUEST,
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
        self, serializer: Serializer
    ) -> Dict[Type[Finding], List[Finding]]:
        findings = {}
        models = importlib.import_module("findings.models")
        for finding_type in serializer.finding_types or FindingName:
            model = getattr(models, finding_type)
            findings[model.__name__.lower()] = [
                {k: v for k, v in model_to_dict(f).items() if k != "executions"}
                for f in model.objects.filter(**serializer.filter).all()
            ]
        return findings

    def _create_report(self, request: Request) -> Tuple[Report, Serializer]:
        serializer = self.get_serializer_class()(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        report = serializer.create(serializer.validated_data)
        return report, serializer

    def _update_report_and_notify(self, report: Report, filename: str) -> None:
        report.path = filename
        report.status = ReportStatus.CREATED
        report.save(update_fields=["path", "status"])
        if hasattr(report.user, "telegram_chat"):
            Telegram().report_created(report)
        SMTP().report_created(report)

    def _json_report(
        self, report: Report, findings: Dict[Type[Finding], List[Finding]]
    ) -> None:
        filename = f"{str(uuid.uuid4())}.json"
        with (CONFIG.generated_reports / filename).open("w") as filepath:
            json.dump(findings, filepath, ensure_ascii=True, indent=4)
        self._update_report_and_notify(report, filename)

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
        self, report: Report, findings: Dict[Type[Finding], List[Finding]]
    ) -> None:
        root = ET.Element("findings")
        for finding_type, finding_list in findings.items():
            for finding in finding_list:
                root.append(
                    self._dict_to_xml(ET.Element(finding_type.lower()), finding)
                )
        ET.indent(root, space="\t")
        filename = f"{str(uuid.uuid4())}.xml"
        with (CONFIG.generated_reports / filename).open("w") as filepath:
            filepath.write(ET.tostring(root, encoding="unicode"))
        self._update_report_and_notify(report, filename)

    def _pdf_report(
        self, report: Report, findings: Dict[Type[Finding], List[Finding]]
    ) -> None:
        # TODO
        pass


# TODO: Create unit tests
