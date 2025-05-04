from datetime import timedelta
from pathlib import Path as PathFile
from typing import Any, Callable, Optional

import requests
from django.utils import timezone
from executions.models import Execution
from findings.enums import PathType, Severity
from findings.framework.models import Finding
from findings.models import Path
from framework.platforms import BaseIntegration
from platforms.defectdojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)
from requests.exceptions import HTTPError
from targets.models import Target


class DefectDojo(BaseIntegration):
    def __init__(self) -> None:
        self.settings = DefectDojoSettings.objects.first()
        self.url = self.settings.server
        super().__init__()
        self.severity_mapping = {
            Severity.INFO: "S0",
            Severity.LOW: "S1",
            Severity.MEDIUM: "S3",
            Severity.HIGH: "S4",
            Severity.CRITICAL: "S5",
        }

    def _request(
        self, method: Callable, url: str, json: bool = True, **kwargs: Any
    ) -> Any:
        return super()._request(
            method,
            f"{self.settings.server}/api/v2{url}",
            json,
            **{
                **kwargs,
                "headers": {
                    "User-Agent": "Rekono",
                    "Authorization": f"Token {self.settings.secret}",
                },
                "verify": self.settings.tls_validation,
            },
        )

    def is_available(self) -> bool:
        if not self.settings.server or not self.settings.secret:
            return False
        if "/api/v2" in self.settings.server:
            self.settings.server = self.settings.server.replace("/api/v2", "")
        if self.settings.server[-1] == "/":
            self.settings.server = self.settings.server[:-1]
        self.settings.save(update_fields=["server"])
        try:
            self._request(requests.get, "/test_types/", timeout=5)
            return True
        except Exception:
            return False

    def exists(self, entity_name: str, id: int) -> bool:
        try:
            self._request(self.session.get, f"/{entity_name}/{id}/")
            return True
        except Exception:
            return False

    def create_product_type(self, name: str, description: str) -> dict[str, Any]:
        return self._request(
            self.session.post,
            "/product_types/",
            data={"name": name, "description": description},
        )

    def create_product(
        self, product_type: int, name: str, description: str, tags: list[str]
    ) -> dict[str, Any]:
        return self._request(
            self.session.post,
            "/products/",
            data={
                "tags": tags,
                "name": name,
                "description": description,
                "prod_type": product_type,
            },
        )

    def create_engagement(
        self, product: int, name: str, description: str, tags: list[str]
    ) -> dict[str, Any]:
        start = timezone.now()
        end = start + timedelta(days=7)
        return self._request(
            self.session.post,
            "/engagements/",
            data={
                "name": name,
                "description": description,
                "tags": tags,
                "product": product,
                "status": "In Progress",
                "engagement_type": "Interactive",
                "target_start": start.strftime(self.settings.date_format),
                "target_end": end.strftime(self.settings.date_format),
            },
        )

    def _create_test_type(self, name: str, tags: list[str]) -> dict[str, Any]:
        return self._request(
            self.session.post,
            "/test_types/",
            data={"name": name, "tags": tags, "dynamic_tool": True},
        )

    def _create_test(
        self, test_type: int, engagement: int, title: str, description: str
    ) -> dict[str, Any]:
        return self._request(
            self.session.post,
            "/tests/",
            data={
                "engagement": engagement,
                "test_type": test_type,
                "title": title,
                "description": description,
                "target_start": timezone.now().strftime(self.settings.datetime_format),
                "target_end": timezone.now().strftime(self.settings.datetime_format),
            },
        )

    def _create_endpoint(
        self, product: int, endpoint: Path, target: Target
    ) -> Optional[dict[str, Any]]:
        try:
            return self._request(
                self.session.post,
                "/endpoints/",
                data={**endpoint.defectdojo_endpoint(target), "product": product},
            )
        except HTTPError:
            return None

    def _create_finding(self, test: int, finding: Finding) -> dict[str, Any]:
        data = finding.defectdojo()
        return self._request(
            self.session.post,
            "/findings/",
            data={
                **data,
                "test": test,
                "numerical_severity": self.severity_mapping[data.get("severity")],
                "active": True,
            },
        )

    def _import_scan(
        self, engagement: int, execution: Execution, tags: list[str]
    ) -> dict[str, Any]:
        with open(execution.output_file, "r") as report:
            return self._request(
                self.session.post,
                "/import-scan/",
                data={
                    "scan_type": execution.configuration.tool.defectdojo_scan_type,
                    "engagement": engagement,
                    "tags": tags,
                },
                files={"file": report},
            )

    def _process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        target_sync = DefectDojoTargetSync.objects.filter(target=execution.task.target)
        if target_sync.exists():
            sync = target_sync.first()
            engagement_id = sync.engagement_id
            product_id = sync.defectdojo_sync.product_id
        else:
            project_sync = DefectDojoSync.objects.filter(
                project=execution.task.target.project
            )
            if project_sync.exists():
                sync = project_sync.first()
                product_id = sync.product_id
                if sync.engagement_id:
                    engagement_id = sync.engagement_id
                else:
                    new_engagement = self.create_engagement(
                        product_id,
                        execution.task.target.target,
                        f"Rekono assessment for {execution.task.target.target}",
                        [self.settings.tag] if self.settings.tag else [],
                    )
                    new_sync = DefectDojoTargetSync.objects.create(
                        defectdojo_sync=sync,
                        target=execution.task.target,
                        engagement_id=new_engagement.get("id"),
                    )
                    engagement_id = new_sync.engagement_id
            else:
                return
        if (
            execution.configuration.tool.defectdojo_scan_type
            and execution.output_file is not None
            and PathFile(execution.output_file).is_file()
        ):
            new_import = self._import_scan(
                engagement_id, execution, [self.settings.tag]
            )
            execution.defectdojo_test_id = new_import.get("test_id")
            execution.save(update_fields=["defectdojo_test_id"])
        else:
            test_id = None
            for finding in findings:
                if isinstance(finding, Path) and finding.type == PathType.ENDPOINT:
                    if finding.defectdojo_id is None:
                        new_endpoint = self._create_endpoint(
                            product_id, finding, execution.task.target
                        )
                        if new_endpoint is not None:
                            finding.defectdojo_id = new_endpoint.get("id")
                else:
                    if not test_id:
                        if not self.settings.test_type_id:
                            new_test_type = self._create_test_type(
                                self.settings.test_type,
                                [self.settings.tag] if self.settings.tag else [],
                            )
                            self.settings.test_type_id = new_test_type.get("id")
                            self.settings.save(update_fields=["test_type_id"])
                        new_test = self._create_test(
                            self.settings.test_type_id,
                            engagement_id,
                            self.settings.test,
                            self.settings.test,
                        )
                        test_id = new_test.get("id")
                    if test_id:
                        new_finding = self._create_finding(test_id, finding)
                        finding.defectdojo_id = new_finding.get("id")
                finding.save(update_fields=["defectdojo_id"])
