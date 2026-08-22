"""Integration with the CVE Crowd trending vulnerability platform."""

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
    """Integration that says which vulnerabilities are being discussed right now.

    Attributes:
        finding_types: Only the vulnerabilities can be trending.
        url: Endpoint that returns the CVEs that are trending.
    """

    finding_types = [Vulnerability]
    url = "https://api.cvecrowd.com/v2/cves"

    @property
    def settings(self) -> CveCrowdSettings:
        """The CVE Crowd configuration, or None if it hasn't been created yet."""
        return CveCrowdSettings.objects.first()

    def is_available(self) -> bool:
        """Check if the platform can be used.

        Returns:
            Whether the platform answered the last time that the API token was
            saved, since checking it on every finding would waste the requests
            that the token allows.
        """
        return self.settings.is_available

    def live_is_available(self) -> bool:
        """Check if the platform answers right now.

        Returns:
            Whether CVE Crowd reports any trending CVE, without using the ones
            that are already stored.
        """
        return len(self.get_trending_cves(False)) > 0

    @cached_property
    def trending_cves(self) -> list[str]:
        """The CVEs that are trending, without asking the platform again."""
        return self.get_trending_cves(True)

    def get_trending_cves(self, use_cache: bool) -> list[str]:
        """Get the CVEs that are trending.

        Args:
            use_cache: Whether the stored CVEs can be used, which they are as long
              as they were reported within the last day.

        Returns:
            The trending CVEs, which are stored so the executions don't ask for
            them again while they process their findings.
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
        """Ask the platform which CVEs are trending, one page at a time.

        Args:
            accumulated: CVEs of the previous pages, which is empty for the first
              one.

        Returns:
            The trending CVEs, or the ones read so far if no API token is
            configured or if a page fails, since half of the list is better than
            nothing.
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
        """Mark a discovered vulnerability as trending.

        Args:
            execution: Execution that discovered the vulnerability.
            finding: Vulnerability to mark, which was already checked to be one of
              the trending ones.
        """
        finding.trending = True
        finding.save(update_fields=["trending"])

    def is_finding_processable(self, finding: Finding) -> bool:
        """Check if this platform can say anything about a finding.

        Args:
            finding: Finding whose type and data are checked.

        Returns:
            Whether the finding is a vulnerability whose CVE is trending, and
            whether the vulnerabilities must be checked as soon as they are
            discovered instead of only by the monitor job.
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
        """Refresh which vulnerabilities are trending and alert about the new ones.

        The vulnerabilities that stop being discussed stop being trending too, so
        the users always see what matters today.
        """
        if not self.is_enabled():
            return
        if not self.trending_cves:
            self.logger.warning("[CVE Crowd] No trending CVEs found")
            return
        # Captured before the trending flags below are updated, so only CVEs that start trending
        # in this run are notified, not the ones that were already trending before it
        already_trending_cves = list(Vulnerability.objects.filter(trending=True).all().values_list("cve", flat=True))
        Vulnerability.objects.filter(trending=True).exclude(cve__in=self.trending_cves).update(trending=False)
        Vulnerability.objects.filter(trending=False, cve__in=self.trending_cves).update(trending=True)
        notifications = [SMTP(), Telegram()]
        # Tracks vulnerabilities already notified across alerts, so the same one isn't notified
        # again when multiple TRENDING_CVE alerts match it within the same project
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
