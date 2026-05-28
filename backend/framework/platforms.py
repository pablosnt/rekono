"""Platform integration classes for external security tools and services.

Provides base classes for integrating with external platforms such as
vulnerability management systems, notification services, and threat
intelligence platforms.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdown import markdown
from requests.adapters import HTTPAdapter, Retry

from alerts.models import Alert
from executions.models import Execution
from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.logging import LoggingEntity
from integrations.models import Integration
from users.enums import Notification


class BasePlatform(LoggingEntity):
    """Base class for external platform integrations.

    Provides common interface for all external platform integrations
    including availability checks and findings processing.
    """

    def is_available(self) -> bool:
        """Check if the platform integration is available.

        Returns:
            bool: True if the platform is available, False otherwise.
        """
        return True

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process findings from an execution.

        Args:
            execution (Execution): The execution that generated the findings.
            findings (list[Finding]): List of findings to process.
        """
        pass


class BaseIntegration(BasePlatform):
    """Base class for external service integrations.

    Extends BasePlatform with HTTP session management, authentication,
    and finding filtering capabilities for external API integrations.

    Security Features:
        - Authenticated HTTP sessions with retry logic
        - Request logging and error handling
        - Finding type filtering for selective processing
        - Integration enable/disable controls

    Attributes:
        url (str): Base URL for the external service.
        finding_types (list): List of Finding types to process (empty = all).
    """

    url = ""
    finding_types = []  # If empty, all findings are processed

    @cached_property
    def integration(self) -> Integration:
        """Get the Integration model instance for this platform.

        Returns:
            Integration: The integration configuration object.
        """
        return Integration.objects.get(key=self.__class__.__name__.lower())

    @cached_property
    def session(self) -> requests.Session:
        """Get configured HTTP session with retry logic.

        Returns:
            requests.Session: Configured session with retry adapter.
        """
        session = requests.Session()
        session.mount(
            f"{urlparse(self.url).scheme}://",
            HTTPAdapter(
                max_retries=Retry(
                    total=10,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504, 599],
                )
            ),
        )
        return session

    def is_enabled(self) -> bool:
        """Check if the integration is enabled.

        Returns:
            bool: True if integration exists and is enabled, False otherwise.
        """
        return self.integration.enabled if self.integration else False

    def _request(
        self,
        method: Callable,
        url: str,
        json: bool = True,
        trigger_exception: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Make HTTP request with logging and error handling.

        Args:
            method (Callable): HTTP method function (get, post, etc.).
            url (str): Request URL.
            json (bool): Whether to parse response as JSON.
            trigger_exception (bool): Whether to raise HTTP exceptions.
            **kwargs (Any): Additional request arguments.

        Returns:
            Any: Response data (JSON dict or Response object).
        """
        try:
            response = method(url, **kwargs)
        except requests.exceptions.ConnectionError:
            response = method(url, **kwargs)
        self.logger.info(
            f"[{self.__class__.__name__}] {method.__name__.upper()} {urlparse(url).path} > HTTP {response.status_code}"
        )
        if trigger_exception:
            response.raise_for_status()
        return response.json() if json else response

    def is_finding_processable(self, finding: Finding) -> bool:
        """Check if a finding should be processed by this integration.

        Args:
            finding (Finding): The finding to check.

        Returns:
            bool: True if finding should be processed, False otherwise.
        """
        return finding.__class__ in self.finding_types or len(self.finding_types) == 0

    def _process_finding(self, execution: Execution, finding: Finding) -> None:
        """Process a single finding (implementation specific).

        Args:
            execution (Execution): The execution that generated the finding.
            finding (Finding): The finding to process.

        Note:
            This method should be overridden by concrete implementations.
        """
        pass

    def process_finding(self, execution: Execution, finding: Finding) -> None:
        """Process a finding with enable and type checks.

        Args:
            execution (Execution): The execution that generated the finding.
            finding (Finding): The finding to process.
        """
        if not self.is_enabled() or not self.is_finding_processable(finding):
            return
        self._process_finding(execution, finding)

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process multiple findings from an execution.

        Args:
            execution (Execution): The execution that generated the findings.
            findings (list[Finding]): List of findings to process.
        """
        if not self.is_enabled():
            return
        for finding in findings:
            self.process_finding(execution, finding)


class BaseCveProvider(BaseIntegration):
    """Base class for CVE enrichment provider integrations.

    Extends BaseIntegration with CVE-specific enrichment logic including
    data retrieval, parsing, quality scoring, and persistence. Concrete
    subclasses implement _get_cve and _parse_cve for each provider API.

    Attributes:
        finding_types (list): Supported finding types (Vulnerability only).
        cvss_mapping (dict): CVSS base score ranges mapped to Rekono severity levels.
    """

    finding_types = [Vulnerability]
    cvss_mapping = {
        Severity.CRITICAL: (9, 11),
        Severity.HIGH: (7, 9),
        Severity.MEDIUM: (4, 7),
        Severity.LOW: (2, 4),
        Severity.INFO: (0, 2),
    }

    @dataclass
    class CveEnrichment:
        """Standardized container for CVE enrichment data returned by providers.

        Attributes:
            name (str | None): Vulnerability name or CISA advisory title.
            description (str | None): Full technical vulnerability description.
            cwe (str | None): CWE identifier in CWE-NNN format.
            cvss_base_score (float | None): Numeric CVSS base score.
            cvss_vector (str | None): Full CVSS vector string.
            cvss_version (str | None): CVSS version prefix (e.g. "3.1", "4.0").
            epss_score (float | None): EPSS probability of exploitation (0.0–1.0).
            epss_percentile (float | None): EPSS percentile rank among all CVEs (0.0–1.0).
            technologies (list[str] | None): Affected product or package identifiers.
            reference (str | None): Canonical vulnerability detail page URL.
            status (str | None): Provider-specific advisory status string.
        """

        name: str | None = None
        description: str | None = None
        cwe: str | None = None
        cvss_base_score: float | None = None
        cvss_vector: str | None = None
        cvss_version: str | None = None
        epss_score: float | None = None
        epss_percentile: float | None = None
        technologies: list[str] | None = None
        reference: str | None = None
        status: str | None = None

    def is_available(self) -> bool:
        """Check if the CVE provider API is reachable and functional.

        Tests connectivity by requesting data for a known CVE (Log4Shell)
        to validate authentication and API availability.

        Returns:
            bool: True if the provider API is reachable and returns data, False otherwise.
        """
        try:
            # Test connectivity using Log4Shell as a well-known, reliably indexed CVE
            self._get_cve("CVE-2021-44228")
            return True
        except Exception:
            return False

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Retrieve raw CVE data from the provider API.

        Args:
            cve (str): CVE identifier to retrieve.

        Returns:
            dict[str, Any]: Raw API response for the CVE.
        """
        return {}  # pragma: no cover

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> CveEnrichment | None:
        """Parse raw provider API response into a CveEnrichment object.

        Args:
            cve (str): CVE identifier being parsed.
            data (list[dict[str, Any]] | dict[str, Any]): Raw API response data.

        Returns:
            CveEnrichment | None: Parsed enrichment data, or None if unavailable.
        """
        return None

    def get_cve(self, cve: str) -> CveEnrichment | None:
        """Retrieve and parse CVE enrichment data from the provider.

        Args:
            cve (str): CVE identifier to enrich.

        Returns:
            CveEnrichment | None: Parsed CVE data, or None if the provider returns nothing.
        """
        data = self._get_cve(cve)
        return self._parse_cve(cve, data) if data else None

    def cve_quality_score(self, data: CveEnrichment) -> int:
        """Calculate a data quality score for CVE enrichment data.

        Scores start at 10 and are adjusted based on CVSS version (older versions
        penalised), presence of CWE and affected technology data, and EPSS availability.
        Subclasses may override to apply provider-specific adjustments.

        Args:
            data (CveEnrichment): CVE enrichment data to score.

        Returns:
            int: Quality score used to select the best provider when multiple match.
        """
        score = 10
        if not data.description:
            score -= 8
        if (
            not data.cvss_base_score
            or not data.cvss_version
            or not data.cvss_vector
            or not data.cwe
            or len(list(data.technologies or [])) == 0
        ):
            score -= 5
        elif data.cvss_version.startswith("2"):
            score -= 2
        if data.epss_score and data.epss_percentile:
            score += 1
        return score

    def save(self, finding: Vulnerability, data: CveEnrichment) -> None:
        """Persist CVE enrichment data onto a Vulnerability finding.

        Updates the finding's name, description, CWE, CVSS fields, EPSS scores,
        and reference with data from the enrichment object. Severity is derived
        from the CVSS base score using the cvss_mapping ranges.

        Args:
            finding (Vulnerability): The vulnerability finding to update.
            data (CveEnrichment): CVE enrichment data to apply.
        """
        finding.name = data.name
        finding.description = (
            BeautifulSoup(markdown(data.description), features="html.parser").get_text()
            if data.description and data.description.startswith("#")
            else data.description
        )
        finding.cwe = data.cwe
        if data.cvss_base_score:
            finding.severity = next(
                (
                    k
                    for k, v in self.cvss_mapping.items()
                    if data.cvss_base_score >= v[0] and data.cvss_base_score < v[1]
                ),
                Severity.MEDIUM,
            )
            finding.cvss_base_score = data.cvss_base_score
        finding.cvss_vector = data.cvss_vector
        finding.cvss_version = data.cvss_version
        finding.epss_score = data.epss_score
        finding.epss_percentile = data.epss_percentile
        finding.reference = data.reference
        finding.save(
            update_fields=[
                "name",
                "description",
                "cwe",
                "severity",
                "cvss_base_score",
                "cvss_vector",
                "cvss_version",
                "epss_score",
                "epss_percentile",
                "reference",
            ]
        )

    def is_finding_processable(self, finding: Finding) -> bool:
        """Determine if a finding can be processed by this integration.

        Validates that the finding is a processable vulnerability type
        with a valid CVE identifier for NVD API queries.

        Args:
            finding (Finding): The finding to evaluate for processing

        Returns:
            bool: True if finding has CVE and can be processed, False otherwise
        """
        return self.is_enabled() and super().is_finding_processable(finding) and finding.cve is not None


class BaseNotification(BasePlatform):
    """Base class for notification platform integrations.

    Provides notification capabilities for executions and alerts through
    various channels like email, Telegram, or other messaging platforms.

    User Management:
        - Per-user notification preferences via enable_field
        - Execution-based notifications with scope filtering
        - Alert-based notifications for subscribers
        - Availability checks before sending notifications

    Attributes:
        enable_field (str): User model field name controlling notification enablement.
    """

    enable_field = ""

    def is_enabled(self, user: Any) -> bool:
        """Check if notifications are enabled for a specific user.

        Args:
            user (Any): The user to check notification preferences for.

        Returns:
            bool: True if notifications are enabled for the user, False otherwise.
        """
        return getattr(user, self.enable_field)

    def _notify(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send notifications to users (implementation specific).

        Args:
            users (list[Any]): List of users to notify.
            *args (Any): Additional notification arguments.
            **kwargs (Any): Additional notification keyword arguments.

        Note:
            This method should be overridden by concrete implementations.
        """
        pass

    def _notify_if_available(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send notifications if the platform is available.

        Args:
            users (list[Any]): List of users to notify.
            *args (Any): Additional notification arguments.
            **kwargs (Any): Additional notification keyword arguments.
        """
        if self.is_available():
            self._notify(users, *args, **kwargs)

    def _notify_if_enabled(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send notifications only to users who have notifications enabled.

        Args:
            users (list[Any]): List of users to potentially notify.
            *args (Any): Additional notification arguments.
            **kwargs (Any): Additional notification keyword arguments.
        """
        if self.is_available():
            for user in users:
                if self.is_enabled(user):
                    self._notify([user], *args, **kwargs)

    def _get_users_to_notify_execution(self, execution: Execution) -> list[Any]:
        """Get list of users to notify about an execution.

        Includes the task executor and project members based on their
        notification preferences and scope settings.

        Args:
            execution (Execution): The execution to notify about.

        Returns:
            list[Any]: List of users who should be notified.
        """
        users = set()
        interested_users = execution.task.target.project.members.filter(
            **{
                self.enable_field: True,
                "notification_scope": Notification.ALL_EXECUTIONS,
            }
        )
        if execution.task.executor:
            if execution.task.executor.notification_scope != Notification.DISABLED and getattr(
                execution.task.executor, self.enable_field
            ):
                users.add(execution.task.executor)
            users.update(interested_users.exclude(id=execution.task.executor.id))
        else:
            users.update(interested_users)
        return list(users)

    def _notify_execution(self, users: list[Any], execution: Execution, findings: list[Finding]) -> None:
        """Send execution notifications to users (implementation specific).

        Args:
            users (list[Any]): List of users to notify.
            execution (Execution): The completed execution.
            findings (list[Finding]): Findings from the execution.

        Note:
            This method should be overridden by concrete implementations.
        """
        pass

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process findings by sending execution notifications.

        Args:
            execution (Execution): The execution that generated the findings.
            findings (list[Finding]): List of findings from the execution.
        """
        if not self.is_available():
            return
        self._notify_execution(self._get_users_to_notify_execution(execution), execution, findings)

    def _get_users_to_notify_alert(self, alert: Alert) -> list[Any]:
        """Get list of users to notify about an alert.

        Args:
            alert (Alert): The alert that was triggered.

        Returns:
            list[Any]: Alert subscribers who have notifications enabled.
        """
        return alert.subscribers.filter(**{self.enable_field: True}).all()

    def _notify_alert(self, users: list[Any], alert: Alert, finding: Finding) -> None:
        """Send alert notifications to users (implementation specific).

        Args:
            users (list[Any]): List of users to notify.
            alert (Alert): The alert that was triggered.
            finding (Finding): The finding that triggered the alert.

        Note:
            This method should be overridden by concrete implementations.
        """
        pass

    def process_alert(self, alert: Alert, finding: Finding) -> None:
        """Process an alert by sending notifications to subscribers.

        Args:
            alert (Alert): The alert that was triggered.
            finding (Finding): The finding that triggered the alert.
        """
        if not self.is_available():
            return
        self._notify_alert(alert.subscribers.filter(**{self.enable_field: True}).all(), alert, finding)
