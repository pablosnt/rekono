"""CVE Crowd platform integration for trending vulnerability analysis.

This module provides the core integration class for the CVE Crowd threat intelligence
platform, enabling real-time trending CVE detection, vulnerability correlation, and
automated alerting for security teams. The integration supports both per-execution
processing and bulk monitoring capabilities for comprehensive threat intelligence.
"""

from functools import cached_property
from typing import Any, Callable

from alerts.enums import AlertItem, AlertMode
from alerts.models import Alert
from executions.models import Execution
from findings.enums import TriageStatus
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration
from platforms.cvecrowd.models import CveCrowdSettings
from platforms.mail.notifications import SMTP
from platforms.telegram_app.notifications import Telegram


class CveCrowd(BaseIntegration):
    """CVE Crowd threat intelligence platform integration.

    Provides comprehensive integration with the CVE Crowd API for real-time
    trending vulnerability detection, analysis, and automated alerting.
    Supports both per-execution vulnerability processing and bulk monitoring
    for proactive threat intelligence and security team notification.

    Attributes:
        finding_types (list): Supported finding types (Vulnerability only)
        url (str): CVE Crowd API endpoint URL
    """

    finding_types = [Vulnerability]
    url = "https://api.cvecrowd.com/api/v1/cves"

    @cached_property
    def settings(self) -> CveCrowdSettings:
        """Get CVE Crowd platform configuration settings from database.

        Returns:
            CveCrowdSettings: Platform configuration instance or None if not configured.
        """
        return CveCrowdSettings.objects.first()

    @cached_property
    def trending_cves(self) -> list[str]:
        """Retrieve and cache trending CVE data from the CVE Crowd API.

        Fetches current trending vulnerability data using the configured API
        credentials and trending analysis timeframe. Results are cached for
        efficient access during vulnerability processing operations.

        Returns:
            list[str]: List of trending CVE identifiers, empty list if unavailable.
        """
        if self.integration.enabled and self.settings.secret:
            try:
                return self._request(
                    self.session.get,
                    self.url,
                    headers={"Authorization": f"Bearer {self.settings.secret}"},
                    params={"days": self.settings.trending_span_days},
                )
            except Exception:
                pass
        return []

    def is_available(self) -> bool:
        """Check if the CVE Crowd platform is available and accessible.

        Validates platform connectivity by checking for valid API credentials
        and successful trending CVE data retrieval.

        Returns:
            bool: True if the platform is available and has trending data, False otherwise.
        """
        if self.settings.secret:
            return len(self.trending_cves) > 0
        return False

    # Needed to mock the method for unit testing
    def _request(
        self,
        method: Callable,
        url: str,
        json: bool = True,
        trigger_exception: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Execute HTTP request to CVE Crowd API.

        Wrapper method for HTTP requests to enable unit testing through
        method mocking while maintaining the same interface as the parent class.

        Args:
            method (Callable): HTTP method function (GET, POST, etc.)
            url (str): Target URL for the request
            json (bool): Parse response as JSON (default True)
            trigger_exception (bool): Raise exceptions on errors (default True)
            **kwargs (Any): Additional request parameters

        Returns:
            Any: API response data
        """
        return super()._request(method, url, json, trigger_exception, **kwargs)

    def _process_finding(self, execution: Execution, finding: Vulnerability) -> None:
        """Process a vulnerability finding by marking it as trending.

        Updates the vulnerability's trending status when it matches the
        current trending CVE data from the CVE Crowd platform.

        Args:
            execution (Execution): The execution that produced the finding
            finding (Vulnerability): The vulnerability finding to process
        """
        finding.trending = True
        finding.save(update_fields=["trending"])

    def is_finding_processable(self, finding: Finding) -> bool:
        """Determine if a finding should be processed for trending analysis.

        Evaluates whether a vulnerability finding meets the criteria for
        trending analysis processing based on CVE data availability,
        execution settings, and trending status.

        Args:
            finding (Finding): The finding to evaluate for processing

        Returns:
            bool: True if the finding should be processed, False otherwise
        """
        if not self.trending_cves:
            return False
        return (
            super().is_finding_processable(finding)
            and self.settings.execute_per_execution
            and finding.cve is not None
            and finding.cve in self.trending_cves
        )

    def monitor(self) -> None:
        """Execute bulk monitoring for trending vulnerabilities across all projects.

        Performs comprehensive monitoring of trending CVE data, updating vulnerability
        trending status, and triggering automated notifications for newly trending
        vulnerabilities across all configured projects and alert rules.
        """
        if not self.trending_cves:
            self.logger.warning("[CVE Crowd] No trending CVEs found")
            return
        already_trending_cves = list(Vulnerability.objects.filter(trending=True).all().values_list("cve", flat=True))
        Vulnerability.objects.filter(trending=True).exclude(cve__in=self.trending_cves).update(trending=False)
        Vulnerability.objects.filter(trending=False, cve__in=self.trending_cves).update(trending=True)
        notifications = [SMTP(), Telegram()]
        notified_vulnerabilities: list[int] = []
        for alert in Alert.objects.filter(item=AlertItem.CVE, mode=AlertMode.MONITOR, enabled=True).all():
            vulnerabilities = (
                Vulnerability.objects.filter(
                    executions__task__target__project=alert.project,
                    cve__isnull=False,
                    is_fixed=False,
                    trending=True,
                )
                .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                .exclude(cve__in=already_trending_cves)
                .exclude(id__in=notified_vulnerabilities)
                .all()
            )
            self.logger.info(
                f"[CVE Crowd] New {vulnerabilities.count()} trending vulnerabilities found in project {alert.project.id}"
            )
            for vulnerability in vulnerabilities:
                if alert.must_be_triggered(None, vulnerability):
                    notified_vulnerabilities.append(vulnerability.id)
                    for platform in notifications:
                        platform.process_alert(alert, vulnerability)
