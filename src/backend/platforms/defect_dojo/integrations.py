import os
from datetime import timedelta
from typing import Any, Dict, List

from django.utils import timezone
from executions.models import Execution
from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Path
from framework.platforms import BaseIntegration
from platforms.defect_dojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)


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
        self, method: callable, url: str, json: bool = True, **kwargs: Any
    ) -> Any:
        url = f"{self.settings.server}/api/v2{url}"
        kwargs.update(
            {
                "headers": {
                    "User-Agent": "Rekono",
                    "Authorization": f"Token {self.settings.api_token}",
                },
                "verify": self.settings.tls_validation,
            }
        )
        super()._request(method, url, json, **kwargs)

    def is_available(self) -> bool:
        if not self.settings.server or not self.settings.api_token:
            return False
        if "/api/v2" in self.settings.server:
            self.settings.server = self.settings.server.replace("/api/v2", "")
        if self.settings.server[-1] == "/":
            self.settings.server = self.settings.server[:-1]
        self.settings.save(update_fields=["server"])
        try:
            self._request(self.session.get, "/test_types/")
            return True
        except:
            return False

    def get_product_type(self, name: str) -> Dict[str, Any]:
        search = self._request(
            self.session.get, "/product_types/", params={"name": name}
        )
        return search["results"][0] if search["results"] else None

    def create_product_type(self, name: str, description: str) -> Dict[str, Any]:
        return self._request(
            self.session.post,
            "/product_types/",
            data={"name": name, "description": description},
        )

    def get_product(self, id: int) -> Dict[str, Any]:
        return self._request(self.session.get, f"/products/{id}/")

    def create_product(
        self, product_type: int, name: str, description: str, tags: List[str]
    ) -> Dict[str, Any]:
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

    def get_engagement(self, id: int) -> Dict[str, Any]:
        return self._request(self.session.get, f"/engagements/{id}/")

    def create_engagement(
        self, product: int, name: str, description: str, tags: List[str]
    ) -> Dict[str, Any]:
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

    def _get_test_type(self, name: str) -> Dict[str, Any]:
        search = self._request(self.session.get, "/test_types/", params={"name": name})
        return search["results"][0] if search["results"] else None

    def _create_test_type(self, name: str, tags: List[str]) -> Dict[str, Any]:
        return self._request(
            self.session.post,
            "/test_types/",
            data={"name": name, "tags": tags, "dynamic_tool": True},
        )

    def _create_test(
        self, test_type: int, engagement: int, title: str, description: str
    ) -> Dict[str, Any]:
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

    def _create_endpoint(self, product: int, endpoint: Path) -> Dict[str, Any]:
        return self._request(
            self.session.post,
            "/endpoints/",
            data={**endpoint.defect_dojo(), "product": product},
        )

    def _create_finding(self, test: int, finding: Finding) -> Dict[str, Any]:
        data = finding.defect_dojo()
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
        self, engagement: int, execution: Execution, tags: List[str]
    ) -> Dict[str, Any]:
        with open(execution.output_file, "r") as report:
            return self._request(
                self.session.post,
                "/import-scan/",
                data={
                    "scan_type": execution.configuration.tool.defect_dojo_scan_type,
                    "engagement": engagement,
                    "tags": tags,
                },
                files={"file": report},
            )

    def process_findings(self, execution: Execution, findings: List[Finding]) -> None:
        super().process_findings(execution, findings)
        target_sync = DefectDojoTargetSync.objects.filter(target=execution.task.target)
        if target_sync.exists():
            sync = target_sync.first()
            engagement_id = sync.engagement_id
            product_id = sync.defect_dojo_sync.product_id
        else:
            project_sync = DefectDojoSync.objects.filter(
                project=execution.task.target.project
            )
            if project_sync.exists():
                sync = project_sync.first()
                product_id = sync.product_id
                if sync.engagement_per_target:
                    new_engagement = self.create_engagement(
                        product_id,
                        execution.task.target.target,
                        f"Rekono assessment for {execution.task.target.target}",
                    )
                    new_sync = DefectDojoTargetSync.objects.create(
                        defect_dojo_sync=sync,
                        target=execution.task.target,
                        engagement_id=new_engagement.get("id"),
                    )
                    engagement_id = new_sync.engagement_id
                else:
                    engagement_id = sync.engagement_id
            else:
                return
        if execution.configuration.tool.defect_dojo_scan_type and os.path.isfile(
            execution.output_file
        ):
            new_import = self._import_scan(
                engagement_id, execution, [self.settings.tag]
            )
            execution.defect_dojo_test_id = new_import.get("test_id")
            execution.save(update_fields=["defect_dojo_test_id"])
        else:
            test_id = None
            for finding in findings:
                if isinstance(finding, Path):
                    new_endpoint = self._create_endpoint(product_id, finding)
                    finding.defect_dojo_id = new_endpoint.get("id")
                else:
                    if not test_id:
                        if not self.settings.test_type_id:
                            new_test_type = self._create_test_type(
                                self.settings.test_type, [self.settings.tag]
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
                    new_finding = self._create_finding(test_id, finding)
                    finding.defect_dojo_id = new_finding.get("id")
                finding.save(update_fields=["defect_dojo_id"])
