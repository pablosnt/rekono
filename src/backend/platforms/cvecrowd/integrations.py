import logging
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
from platforms.telegram_app.notifications.notifications import Telegram

logger = logging.getLogger()


class CveCrowd(BaseIntegration):
    finding_types = [Vulnerability]

    def __init__(self) -> None:
        self.settings = CveCrowdSettings.objects.first()
        self.url = "https://api.cvecrowd.com/api/v1/cves"
        self.trending_cves: list[str] = []
        super().__init__()

    def is_available(self) -> bool:
        if self.settings.secret:
            self._get_trending_cves()
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
        return super()._request(method, url, json, trigger_exception, **kwargs)

    def _get_trending_cves(self) -> None:
        if self.integration.enabled and self.settings.secret and len(self.trending_cves) == 0:
            try:
                self.trending_cves = self._request(
                    self.session.get,
                    self.url,
                    headers={"Authorization": f"Bearer {self.settings.secret}"},
                    params={"days": self.settings.trending_span_days},
                )
            except Exception:
                pass

    def _process_finding(self, execution: Execution, finding: Vulnerability) -> None:
        finding.trending = True
        finding.save(update_fields=["trending"])

    def is_finding_processable(self, finding: Finding) -> bool:
        self._get_trending_cves()
        if not self.trending_cves:
            return False
        return (
            super().is_finding_processable(finding)
            and self.settings.execute_per_execution
            and finding.cve is not None
            and finding.cve in self.trending_cves
        )

    def monitor(self) -> None:
        self._get_trending_cves()
        if not self.trending_cves:
            logger.warn("[CVE Crowd] No trending CVEs found")
            return
        already_trending_queryset = Vulnerability.objects.filter(trending=True).all()
        already_trending_cves = list(already_trending_queryset.values_list("cve", flat=True))
        already_trending_queryset.exclude(cve__in=self.trending_cves).update(trending=False)
        Vulnerability.objects.filter(trending=False, cve__in=self.trending_cves).update(trending=True)
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
            logger.info(
                f"[CVE Crowd] New {vulnerabilities.count()} trending vulnerabilities found in project {alert.project.id}"
            )
            for vulnerability in vulnerabilities:
                if alert.must_be_triggered(None, vulnerability):
                    notified_vulnerabilities.append(vulnerability.id)
                    for platform in [SMTP, Telegram]:
                        platform().process_alert(alert, vulnerability)
