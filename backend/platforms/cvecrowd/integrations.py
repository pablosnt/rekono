"""CVE Crowd platform integration for trending vulnerability analysis.

This module provides the core integration class for the CVE Crowd threat intelligence
platform, enabling real-time trending CVE detection, vulnerability correlation, and
automated alerting for security teams. The integration supports both per-execution
processing and bulk monitoring capabilities for comprehensive threat intelligence.
"""

from datetime import timedelta
from functools import cached_property

from django.utils import timezone

from alerts.enums import AlertItem
from alerts.models import Alert
from executions.models import Execution
from findings.enums import TriageStatus
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration
from platforms.cvecrowd.models import CveCrowdCache, CveCrowdSettings
from platforms.email.notifications import SMTP
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
    url = "https://api.cvecrowd.com/v2/cves"

    @property
    def settings(self) -> CveCrowdSettings:
        """Get CVE Crowd platform configuration settings from database.

        Returns:
            CveCrowdSettings: Platform configuration instance or None if not configured.
        """
        return CveCrowdSettings.objects.first()

    def is_available(self) -> bool:
        """Check if the CVE Crowd platform is available and accessible.

        Returns the availability status stored in the database, which is updated
        each time the platform settings are saved.

        Returns:
            bool: True if the platform is available and has trending data, False otherwise.
        """
        return self.settings.is_available

    def live_is_available(self) -> bool:
        """Check if the CVE Crowd platform is available by performing a live API request.

        Validates platform connectivity by fetching trending CVE data directly from
        the API, bypassing the database cache. Returns True if at least one trending
        CVE is returned.

        Returns:
            bool: True if the platform is reachable and returns trending data, False otherwise.
        """
        return len(self.get_trending_cves(False)) > 0

    @cached_property
    def trending_cves(self) -> list[str]:
        """Trending CVEs from CVE Crowd, cached for the lifetime of the instance.

        Uses the database cache to avoid redundant API requests. Delegates to
        get_trending_cves with cache enabled.

        Returns:
            list[str]: List of CVE identifiers currently trending on CVE Crowd.
        """
        return self.get_trending_cves(True)

    def get_trending_cves(self, use_cache: bool) -> list[str]:
        """Retrieve the list of trending CVEs from CVE Crowd, optionally using the database cache.

        When cache is enabled, returns stored CVE data if it was collected within the last day.
        If the cache is expired or empty, fetches fresh data from the API, stores it in the
        database, and returns the result.

        Args:
            use_cache (bool): Whether to use the database cache to avoid redundant API requests.

        Returns:
            list[str]: List of CVE identifiers currently trending on CVE Crowd.
        """
        if use_cache:
            cache = CveCrowdCache.objects.order_by("date")
            if cache.exists():
                first = cache.first()
                if first.date > (timezone.now() - timedelta(days=1)):
                    return cache.values_list("cve", flat=True)
        CveCrowdCache.objects.all().delete()
        cves = self.download_trending_cves()
        if len(cves) > 0:
            CveCrowdCache.objects.bulk_create([CveCrowdCache(cve=cve, date=timezone.now()) for cve in cves])
        return cves

    def download_trending_cves(self, accumulated: list[str] = []) -> list[str]:
        """Download the list of trending CVEs directly from the CVE Crowd API.

        Makes an authenticated request to the CVE Crowd API endpoint, passing the
        configured trending span in days. Returns an empty list if no API token is
        configured or if the request fails.

        Args:
            accumulated (list[str]): Already retrieved CVEs from previous pages.

        Returns:
            list[str]: List of CVE identifiers currently trending on CVE Crowd,
                or an empty list on failure.
        """
        if self.settings.secret:
            params = {"days": self.settings.trending_span_days, "limit": 50}
            if len(accumulated) > 0:
                params["offset"] = len(accumulated)
            try:
                response = self._request(
                    self.session.get,
                    self.url,
                    headers={"Authorization": f"Bearer {self.settings.secret}"},
                    params=params,
                )
                if len(response) == params["limit"]:
                    return self.download_trending_cves(accumulated + response)
                else:
                    return accumulated + response
            except Exception:
                return accumulated
        return accumulated

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
        if not self.is_enabled():
            return
        if not self.trending_cves:
            self.logger.warning("[CVE Crowd] No trending CVEs found")
            return
        already_trending_cves = list(Vulnerability.objects.filter(trending=True).all().values_list("cve", flat=True))
        Vulnerability.objects.filter(trending=True).exclude(cve__in=self.trending_cves).update(trending=False)
        Vulnerability.objects.filter(trending=False, cve__in=self.trending_cves).update(trending=True)
        notifications = [SMTP(), Telegram()]
        notified_vulnerabilities: list[int] = []
        for alert in Alert.objects.filter(item=AlertItem.TRENDING_CVE, enabled=True).all():
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
