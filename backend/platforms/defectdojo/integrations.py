"""DefectDojo integration client for vulnerability management synchronization.

Provides integration with OWASP DefectDojo vulnerability management platform,
enabling automated security finding synchronization through native scan import
and reimport endpoints for centralized vulnerability tracking.
"""

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
    """DefectDojo integration client for vulnerability management synchronization.

    Integrates with OWASP DefectDojo through REST API interactions, pushing security
    findings to DefectDojo after each tool execution. This is an outbound integration,
    Rekono only creates or updates data in DefectDojo, it never reads findings back.
    Supports both native scan file imports (for tools with a registered DefectDojo scan
    type) and generic JSON finding imports, with optional reimport to update existing
    tests instead of creating new ones.

    Processing Features:
        - Outbound synchronization of security findings after each tool execution
        - Native scan file import for tools with a registered DefectDojo scan type
        - Generic JSON finding import for tools without a native DefectDojo scan type
        - Automatic engagement creation when no engagement is configured for the target
        - Optional reimport into an existing test instead of creating a new one

    Attributes:
        generic_import (str): DefectDojo scan type name for generic finding imports.
    """

    generic_import = "Generic Findings Import"

    @property
    def settings(self) -> DefectDojoSettings:
        """Get DefectDojo integration configuration settings from database.

        Returns:
            DefectDojoSettings: DefectDojo configuration instance or None if not configured.
        """
        return DefectDojoSettings.objects.first()

    @cached_property
    def url(self) -> str:
        """Get DefectDojo server URL from configuration settings.

        Returns:
            str: DefectDojo server base URL for API communications
        """
        return self.settings.server

    def _request(
        self,
        method: Callable,
        url: str,
        json: bool = True,
        trigger_exception: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Execute authenticated HTTP request to DefectDojo API.

        Performs HTTP request to DefectDojo API v2 with proper authentication
        headers, TLS validation, and error handling. Automatically constructs
        full API URL and includes necessary security headers.

        Args:
            method (Callable): HTTP method function (requests.get, requests.post, etc.)
            url (str): API endpoint path relative to /api/v2
            json (bool): Whether to parse response as JSON (default True)
            trigger_exception (bool): Whether to raise exceptions on errors (default True)
            **kwargs: Additional arguments passed to the HTTP method

        Returns:
            Any: Response data (JSON dict if json=True, Response object otherwise)
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
        """Check if DefectDojo integration is available and properly configured.

        Validates DefectDojo configuration and tests connectivity to the DefectDojo
        server by attempting to access a simple API endpoint. Ensures all required
        settings are present before testing connection.

        Returns:
            bool: True if DefectDojo is available and functional, False otherwise
        """
        if not self.settings.server or not self.settings.secret:
            return False
        try:
            self._request(requests.get, "/test_types/", timeout=5)
            return True
        except Exception:
            return False

    def exists(self, entity_name: str, id: int) -> tuple[dict[str, Any] | None, bool]:
        """Check if a DefectDojo entity exists by ID.

        Verifies the existence of a DefectDojo entity (product type, product,
        engagement, etc.) by attempting to retrieve it via the API.

        Args:
            entity_name (str): DefectDojo entity type name (plural form)
            id (int): DefectDojo entity ID to check

        Returns:
            tuple[dict[str, Any] | None, bool]: The response and a flag indicating whether the
                                                entity exists
        """
        try:
            response = self._request(self.session.get, f"/{entity_name}/{id}/")
            return response, True
        except Exception:
            return None, False

    def create_engagement(
        self, product: int, name: str, description: str, tags: list[str]
    ) -> dict[str, Any]:  # pragma: no cover
        """Create a new engagement in DefectDojo under a specific product.

        Creates an engagement representing a specific security assessment or testing
        period within a product. Engagements contain tests and findings related to
        a particular security testing activity with defined start and end dates.

        Args:
            product (int): DefectDojo product ID
            name (str): Engagement name
            description (str): Engagement description
            tags (list[str]): List of tags for engagement organization

        Returns:
            dict[str, Any]: DefectDojo API response containing created engagement data
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
        """Look up a DefectDojo test type by name.

        Args:
            name (str): Test type name to search for.

        Returns:
            dict[str, Any] | None: First matching test type record, or None if not found.
        """
        response = self._request(self.session.get, "/test_types/", params={"name": name})
        return response.get("results", [])[0] if response.get("count", 0) > 0 else None

    def _get_test(self, engagement: int, test_type: int, scan_type: str) -> dict[str, Any] | None:
        """Look up an existing DefectDojo test by engagement, test type, and scan type.

        Args:
            engagement (int): DefectDojo engagement ID.
            test_type (int): DefectDojo test type ID.
            scan_type (str): Scan type name matching the tool's DefectDojo scan type.

        Returns:
            dict[str, Any] | None: First matching test record, or None if not found.
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
        """Import or reimport a scan report into DefectDojo.

        Uses `import-scan` when no existing test is provided, creating a new test
        under the given engagement. Uses `reimport-scan` when a test ID is provided,
        updating an existing test and closing findings absent from the new report
        when `close_old_findings` is enabled.

        Args:
            scan_type (str): DefectDojo scan type identifier for the report format.
            report (PathFile): Path to the report file to upload.
            service (str): Service label (target, optionally with port) stored on the test.
            engagement (int): DefectDojo engagement ID.
            test (int | None): Existing DefectDojo test ID for reimport, or None for import.
            tags (list[str]): Tags applied to the created test, findings, and endpoints.
            close_old_findings (bool): Close findings from previous imports not present in this one.

        Returns:
            dict[str, Any]: DefectDojo API response containing the test ID and import summary.
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
        """Synchronize security findings to DefectDojo after execution completion.

        Excludes Path findings, which are only used to build endpoint data for other
        finding types, and findings the user entered manually rather than ones a tool
        detected. Resolves the engagement to push to, from an existing target sync, the
        project sync, or a newly created one, then imports the remaining findings as a
        scan report. For tools with a registered DefectDojo scan type the raw output file
        is sent; otherwise a Generic Findings Import JSON is built from the finding data.
        If neither a target sync nor a project sync exists for the execution's target,
        the findings are left unsynchronized and the method returns without error. When
        the project sync has reimport enabled, an existing test is located and updated
        instead of creating a new one, except right after an engagement was just created
        for this call, since a brand new engagement cannot already contain a test.

        Args:
            execution (Execution): Completed security tool execution.
            findings (list[Finding]): Security findings to synchronize.
        """
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
        """Synchronize findings to DefectDojo, guarding availability and errors.

        Public entry point that skips processing when the integration is disabled
        or unavailable and delegates the actual scan import to _process_findings.
        Any failure during the import is logged rather than propagated, so a
        DefectDojo outage never interrupts the rest of the execution pipeline.

        Args:
            execution (Execution): Completed security tool execution.
            findings (list[Finding]): Security findings to synchronize.
        """
        if not self.is_enabled() or not self.is_available():
            return
        try:
            return self._process_findings(execution, findings)
        except Exception as ex:
            self.logger.error(
                f"[{self.__class__.__name__}] Error processing {len(findings)} findings from execution {execution.id}: {str(ex)}"
            )
