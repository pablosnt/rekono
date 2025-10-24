"""DefectDojo integration client for vulnerability management synchronization.

Provides comprehensive integration with OWASP DefectDojo vulnerability management
platform, enabling automated security finding synchronization, entity creation,
and bidirectional data flow for streamlined vulnerability tracking and reporting.
"""

from datetime import timedelta
from functools import cached_property
from pathlib import Path as PathFile
from typing import Any, Callable

import requests
from django.utils import timezone

from executions.models import Execution
from findings.enums import PathType, Severity
from findings.framework.models import Finding
from findings.models import Path
from framework.platforms import BaseIntegration
from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync, DefectDojoTargetSync
from targets.models import Target


class DefectDojo(BaseIntegration):
    """DefectDojo integration client for vulnerability management synchronization.

    Provides comprehensive integration with OWASP DefectDojo vulnerability management
    platform through REST API interactions. Supports automated finding synchronization,
    hierarchical entity management, and bidirectional data flow for centralized
    vulnerability tracking and reporting workflows.

    Integration Features:
        - Automated vulnerability finding synchronization after tool execution
        - Support for both scan file imports and generic finding creation
        - Hierarchical entity management (Product Types → Products → Engagements → Tests)
        - Real-time availability checking and connection validation
        - Severity mapping between Rekono and DefectDojo severity scales
        - Project-level and target-level engagement organization

    Data Synchronization:
        - Security findings mapped to DefectDojo finding format
        - Web endpoints synchronized for application security testing
        - Execution results linked to DefectDojo tests for audit trails
        - Tag-based organization and filtering capabilities

    Attributes:
        run_per_execution (bool): Execute integration after each tool execution
        severity_mapping (dict): Mapping between Rekono and DefectDojo severity levels
    """

    run_per_execution = True
    severity_mapping = {
        Severity.INFO: "S0",
        Severity.LOW: "S1",
        Severity.MEDIUM: "S3",
        Severity.HIGH: "S4",
        Severity.CRITICAL: "S5",
    }

    @cached_property
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

    def exists(self, entity_name: str, id: int) -> bool:
        """Check if a DefectDojo entity exists by ID.

        Verifies the existence of a DefectDojo entity (product type, product,
        engagement, etc.) by attempting to retrieve it via the API.

        Args:
            entity_name (str): DefectDojo entity type name (plural form)
            id (int): DefectDojo entity ID to check

        Returns:
            bool: True if entity exists, False otherwise
        """
        try:
            self._request(self.session.get, f"/{entity_name}/{id}/")
            return True
        except Exception:
            return False

    def create_product_type(self, name: str, description: str) -> dict[str, Any]:  # pragma: no cover
        """Create a new product type in DefectDojo.

        Creates a top-level organizational entity in DefectDojo's hierarchy.
        Product types serve as the highest level of organization for grouping
        related products and security assessments.

        Args:
            name (str): Product type name
            description (str): Product type description

        Returns:
            dict[str, Any]: DefectDojo API response containing created product type data
        """
        return self._request(self.session.post, "/product_types/", data={"name": name, "description": description})

    def create_product(
        self, product_type: int, name: str, description: str, tags: list[str]
    ) -> dict[str, Any]:  # pragma: no cover
        """Create a new product in DefectDojo under a specific product type.

        Creates a product entity representing a specific application or system
        being tested. Products are associated with product types and can have
        multiple engagements for different security assessments.

        Args:
            product_type (int): DefectDojo product type ID
            name (str): Product name
            description (str): Product description
            tags (list[str]): List of tags for product organization

        Returns:
            dict[str, Any]: DefectDojo API response containing created product data
        """
        return self._request(
            self.session.post,
            "/products/",
            data={"tags": tags, "name": name, "description": description, "prod_type": product_type},
        )

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

    def _create_test_type(self, name: str, tags: list[str]) -> dict[str, Any]:  # pragma: no cover
        """Create a new test type in DefectDojo for categorizing tests.

        Creates a test type definition that can be reused across multiple tests.
        Test types help categorize and organize different kinds of security
        assessments within DefectDojo.

        Args:
            name (str): Test type name
            tags (list[str]): List of tags for test type organization

        Returns:
            dict[str, Any]: DefectDojo API response containing created test type data
        """
        return self._request(self.session.post, "/test_types/", data={"name": name, "tags": tags, "dynamic_tool": True})

    def _create_test(
        self, test_type: int, engagement: int, title: str, description: str
    ) -> dict[str, Any]:  # pragma: no cover
        """Create a new test in DefectDojo under a specific engagement.

        Creates a test entity representing a specific security testing activity.
        Tests contain individual findings and serve as containers for organizing
        security vulnerabilities discovered during assessments.

        Args:
            test_type (int): DefectDojo test type ID
            engagement (int): DefectDojo engagement ID
            title (str): Test title
            description (str): Test description

        Returns:
            dict[str, Any]: DefectDojo API response containing created test data
        """
        datetime = timezone.now().strftime(self.settings.datetime_format)
        return self._request(
            self.session.post,
            "/tests/",
            data={
                "engagement": engagement,
                "test_type": test_type,
                "title": title,
                "description": description,
                "target_start": datetime,
                "target_end": datetime,
            },
        )

    def _create_endpoint(
        self, product: int, endpoint: Path, target: Target
    ) -> dict[str, Any] | None:  # pragma: no cover
        """Create a new endpoint in DefectDojo for web application testing.

        Creates an endpoint entity representing a specific web service or API
        endpoint discovered during security testing. Endpoints are associated
        with products and help track web application attack surface.

        Args:
            product (int): DefectDojo product ID
            endpoint (Path): Path finding containing endpoint information
            target (Target): Target being assessed

        Returns:
            dict[str, Any] | None: DefectDojo API response with endpoint data or None on error
        """
        # TOTEST: What happen if the endpoint already exists?
        return self._request(
            self.session.post, "/endpoints/", data={**endpoint.defectdojo_endpoint(target), "product": product}
        )

    def _create_finding(self, test: int, finding: Finding) -> dict[str, Any]:  # pragma: no cover
        """Create a new finding in DefectDojo under a specific test.

        Creates a security finding representing a discovered vulnerability or
        security issue. Findings are the core entities in DefectDojo containing
        detailed vulnerability information, severity, and remediation guidance.

        Args:
            test (int): DefectDojo test ID
            finding (Finding): Rekono finding to be synchronized

        Returns:
            dict[str, Any]: DefectDojo API response containing created finding data
        """
        data = finding.defectdojo_finding()
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
    ) -> dict[str, Any]:  # pragma: no cover
        """Import scan results file directly into DefectDojo.

        Imports security tool output files directly into DefectDojo using the
        native scan import functionality. This preserves original tool output
        format and leverages DefectDojo's built-in parsers for comprehensive
        finding extraction and analysis.

        Args:
            engagement (int): DefectDojo engagement ID
            execution (Execution): Rekono execution containing scan results
            tags (list[str]): List of tags for imported findings

        Returns:
            dict[str, Any]: DefectDojo API response containing import results
        """
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

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process and synchronize security findings to DefectDojo after execution completion.

        Main integration method that handles the complete synchronization workflow
        for security findings discovered during tool execution. Manages the hierarchical
        organization of findings within DefectDojo's structure and supports both
        scan file imports and generic finding creation.

        Synchronization Workflow:
            1. Determine target or project-level synchronization configuration
            2. Create engagement if needed for new targets
            3. Import scan results if tool supports native DefectDojo format
            4. Create generic findings and endpoints for structured data
            5. Update DefectDojo entity IDs for future reference

        Args:
            execution (Execution): Completed security tool execution
            findings (list[Finding]): List of security findings to synchronize
        """
        target_sync = DefectDojoTargetSync.objects.filter(target=execution.task.target)
        if target_sync.exists():
            sync = target_sync.first()
            engagement_id = sync.engagement_id
            product_id = sync.defectdojo_sync.product_id
        else:
            project_sync = DefectDojoSync.objects.filter(project=execution.task.target.project)
            if not project_sync.exists():
                return
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
                    defectdojo_sync=sync, target=execution.task.target, engagement_id=new_engagement.get("id")
                )
                engagement_id = new_sync.engagement_id
        if (
            execution.configuration.tool.defectdojo_scan_type
            and execution.output_file is not None
            and PathFile(execution.output_file).is_file()
        ):
            new_import = self._import_scan(engagement_id, execution, [self.settings.tag])
            execution.defectdojo_test_id = new_import.get("test_id")
            execution.save(update_fields=["defectdojo_test_id"])
        else:
            test_id = None
            for finding in findings:
                if finding.created_from_user_input:
                    continue
                if isinstance(finding, Path) and finding.type == PathType.ENDPOINT:
                    if finding.defectdojo_id is None:
                        new_endpoint = self._create_endpoint(product_id, finding, execution.task.target)
                        if new_endpoint is not None:
                            finding.defectdojo_id = new_endpoint.get("id")
                else:
                    if not test_id:
                        if not self.settings.test_type_id:
                            new_test_type = self._create_test_type(
                                self.settings.test_type, [self.settings.tag] if self.settings.tag else []
                            )
                            self.settings.test_type_id = new_test_type.get("id")
                            self.settings.save(update_fields=["test_type_id"])
                        new_test = self._create_test(
                            self.settings.test_type_id, engagement_id, self.settings.test, self.settings.test
                        )
                        test_id = new_test.get("id")
                    if test_id:
                        new_finding = self._create_finding(test_id, finding)
                        finding.defectdojo_id = new_finding.get("id")
                finding.save(update_fields=["defectdojo_id"])
