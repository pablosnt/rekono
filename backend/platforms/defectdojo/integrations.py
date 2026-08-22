"""Integration with the DefectDojo vulnerability management platform."""

import json
import uuid
from datetime import timedelta
from functools import cached_property
from pathlib import Path as PathFile
from typing import Any, Callable

import requests
from django.utils import timezone

from executions.models import Execution
from findings.framework.models import Finding
from findings.models import Path
from framework.platforms import BaseIntegration
from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync, DefectDojoTargetSync
from rekono.settings import CONFIG


class DefectDojo(BaseIntegration):
    """Integration that sends the findings of each execution to DefectDojo.

    Nothing is ever read back from DefectDojo, Rekono only writes in it, so the
    findings of both platforms can't get out of sync.

    Attributes:
        generic_import: Format that DefectDojo accepts from the tools whose reports
          it doesn't understand.
    """

    generic_import = "Generic Findings Import"

    @property
    def settings(self) -> DefectDojoSettings:
        """The DefectDojo configuration, or None if it hasn't been created yet."""
        return DefectDojoSettings.objects.first()

    @cached_property
    def url(self) -> str:
        """The URL of the DefectDojo server, which the users configure."""
        return self.settings.server

    def _request(
        self,
        method: Callable,
        url: str,
        json: bool = True,
        trigger_exception: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the DefectDojo API.

        Args:
            method: Method of the session that sends the request.
            url: Path of the endpoint, without the URL of the API.
            json: Whether the response must be parsed as JSON.
            trigger_exception: Whether a failed request must raise an exception.
            **kwargs: Extra arguments for the request, like its parameters.

        Returns:
            The response of the server, with the API token already included in the
            request, and with the TLS certificate validated or not depending on
            the configuration, since a DefectDojo can be deployed with a self
            signed certificate.
        """
        return super()._request(  # pragma: no cover
            method,
            f"{self.settings.server}/api/v2{url}",
            json,
            trigger_exception,
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
        """Check if the platform can be used.

        Returns:
            Whether a server and an API token are configured, and whether that
            server answers to them.
        """
        if not self.settings.server or not self.settings.secret:
            return False
        try:
            self._request(requests.get, "/test_types/", timeout=5)
            return True
        except Exception:
            return False

    def exists(self, entity_name: str, id: int) -> tuple[dict[str, Any] | None, bool]:
        """Check if something exists in DefectDojo, like a product or an engagement.

        Args:
            entity_name: Kind of thing to look for, in plural, as its endpoint.
            id: Identifier that it has in DefectDojo.

        Returns:
            The thing that was found and whether it exists, so the users can't
            configure a synchronization against something that isn't there.
        """
        try:
            response = self._request(self.session.get, f"/{entity_name}/{id}/")
            return response, True
        except Exception:
            return None, False

    def create_engagement(
        self, product: int, name: str, description: str, tags: list[str]
    ) -> dict[str, Any]:  # pragma: no cover
        """Create an engagement in a DefectDojo product.

        Args:
            product: Product that the engagement belongs to.
            name: Name of the engagement.
            description: Explanation of what the engagement covers.
            tags: Tags that classify the engagement.

        Returns:
            The created engagement, which lasts one week, since DefectDojo requires
            an engagement to have an end date.
        """
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

    def _get_test_type(self, name: str) -> dict[str, Any] | None:
        """Find a test type in DefectDojo by its name.

        Args:
            name: Name of the test type, which is the name of a tool.

        Returns:
            The test type, or None if DefectDojo doesn't have one for that tool.
        """
        response = self._request(self.session.get, "/test_types/", params={"name": name})
        return response.get("results", [])[0] if response.get("count", 0) > 0 else None

    def _get_test(self, engagement: int, test_type: int, scan_type: str) -> dict[str, Any] | None:
        """Find the test of an engagement that a report can be added to.

        Args:
            engagement: Engagement where the test is searched.
            test_type: Test type that the test must have.
            scan_type: Report format that the test must accept.

        Returns:
            The test, or None if the engagement has no test for that tool yet.
        """
        response = self._request(
            self.session.get,
            "/tests/",
            params={"engagement": engagement, "scan_type": scan_type, "test_type": test_type},
        )
        return response.get("results", [])[0] if response.get("count", 0) > 0 else None

    def _import_or_reimport_scan(
        self,
        scan_type: str,
        report: PathFile,
        service: str,
        engagement: int,
        test: int | None,
        tags: list[str],
        close_old_findings: bool,
    ) -> dict[str, Any]:  # pragma: no cover
        """Send a report to DefectDojo, in a new test or in an existing one.

        Args:
            scan_type: Format of the report, as DefectDojo names it.
            report: File with the findings to send.
            service: What was scanned, which is the target and its port.
            engagement: Engagement where a new test is created.
            test: Test where the report is added, or None to create a new one.
            tags: Tags that classify the test and everything imported from it.
            close_old_findings: Whether the findings of the test that this report
              doesn't include must be closed.

        Returns:
            The result of the import, with the identifier of the test that the
            findings ended up in.
        """
        context = {"engagement": engagement}
        endpoint = "import-scan"
        if test:
            context = {"test": test}
            endpoint = "reimport-scan"
        with report.open("r") as _report:
            return self._request(
                self.session.post,
                f"/{endpoint}/",
                data={
                    "scan_type": scan_type,
                    **context,
                    "service": service,
                    "tags": tags,
                    "apply_tags_to_findings": True,
                    "apply_tags_to_endpoints": True,
                    "close_old_findings": close_old_findings,
                },
                files={"file": _report},
            )

    def _process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Send the findings of an execution to the DefectDojo engagement of its target.

        Nothing is sent if neither the target nor its project is synchronized with
        DefectDojo, since there would be nowhere to send it to.

        Args:
            execution: Execution that discovered the findings.
            findings: Findings to send.
        """
        # The paths are only used to build the endpoints of the other findings, and the
        # findings created by the users were never discovered by a tool
        findings = [
            finding for finding in findings if not isinstance(finding, Path) and not finding.created_from_user_input
        ]
        if len(findings) == 0:
            return
        created_engagement = False
        target_sync = DefectDojoTargetSync.objects.filter(target=execution.task.target).first()
        if target_sync:
            engagement_id = target_sync.engagement_id
            product_id = target_sync.defectdojo_sync.product_id
            project_sync = target_sync.defectdojo_sync
        else:
            project_sync = DefectDojoSync.objects.filter(project=execution.task.target.project).first()
            if not project_sync:
                # No sync configured at either level for this target, so there is nothing to push to
                return
            product_id = project_sync.product_id
            if project_sync.engagement_id:
                engagement_id = project_sync.engagement_id
            else:
                created_engagement = True
                new_engagement = self.create_engagement(
                    product_id,
                    execution.task.target.target,
                    f"Rekono assessment for {execution.task.target.target}",
                    [self.settings.tag] if self.settings.tag else [],
                )
                # Persisted as a target sync so later executions for this target reuse the same
                # engagement directly, without creating a new one on every execution
                new_sync = DefectDojoTargetSync.objects.create(
                    defectdojo_sync=project_sync, target=execution.task.target, engagement_id=new_engagement.get("id")
                )
                engagement_id = new_sync.engagement_id
        test_id = None
        # DefectDojo understands the reports of many tools, and the findings of the rest are
        # sent in the generic format that it accepts from anything
        if execution.configuration.tool.defectdojo_scan_type:
            if execution.output_file is None or not PathFile(execution.output_file).is_file():
                # The native report file is required for a native import, so skip silently if it is gone
                return
            scan_type = execution.configuration.tool.defectdojo_scan_type
            test_type_name = scan_type
            report = PathFile(execution.output_file)
        else:
            scan_type = self.generic_import
            report = CONFIG.reports / f"temp-{str(uuid.uuid4())}.json"
            with report.open("w") as temp:
                json.dump(
                    {
                        "name": execution.configuration.tool.name,
                        "type": execution.configuration.tool.name,
                        "findings": [finding.defectdojo_finding() for finding in findings],
                    },
                    temp,
                    ensure_ascii=True,
                    indent=4,
                )
            test_type_name = f"{execution.configuration.tool.name} ({scan_type})"
        try:
            # A brand new engagement can't have a test yet, so it's not even searched for
            if project_sync.reimport and not created_engagement:
                test_type = self._get_test_type(test_type_name)
                if test_type:
                    test = self._get_test(engagement_id, test_type.get("id"), scan_type)
                    test_id = test.get("id") if test else None
            execution.defectdojo_test_id = self._import_or_reimport_scan(
                scan_type,
                report,
                f"{execution.task.target.target}:{execution.task.target_port.port}"
                if execution.task.target_port
                else execution.task.target.target,
                engagement_id,
                test_id,
                [self.settings.tag],
                project_sync.close_old_findings,
            ).get("test_id")
            execution.save(update_fields=["defectdojo_test_id"])
        finally:
            # Only the generic-import path writes a temp file, the native output file must be kept
            if not execution.output_file and report and report.is_file():
                report.unlink()

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Send the findings of an execution to DefectDojo, if it can be used.

        A failure is logged instead of being propagated, so a DefectDojo that is
        down doesn't stop the rest of the platforms.

        Args:
            execution: Execution that discovered the findings.
            findings: Findings to send.
        """
        if not self.is_enabled() or not self.is_available():
            return
        try:
            return self._process_findings(execution, findings)
        except Exception as ex:
            self.logger.error(
                f"[{self.__class__.__name__}] Error processing {len(findings)} findings from execution {execution.id}: {str(ex)}"
            )
