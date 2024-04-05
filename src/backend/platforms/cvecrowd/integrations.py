import logging
from typing import List

from alerts.enums import AlertItem, AlertMode
from alerts.models import Alert
from executions.models import Execution
from findings.enums import TriageStatus
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration
from platforms.cvecrowd.models import CVECrowdSettings
from platforms.mail.notifications import SMTP
from platforms.telegram_app.notifications.notifications import Telegram

logger = logging.getLogger()


class CVECrowd(BaseIntegration):
    def __init__(self) -> None:
        self.settings = CVECrowdSettings.objects.first()
        self.url = "https://api.cvecrowd.com/api/v1/cves"
        super().__init__()

    def _get_trending_cves(self) -> List[str]:
        if self.integration.enabled and self.settings.secret:
            try:
                return self._request(
                    self.url,
                    headers={"Authorization": f"Bearer {self.settings.secret}"},
                    params={"days": self.settings.trending_span_days},
                )
            except:
                pass
        return []

    def process_findings(self, execution: Execution, findings: List[Finding]) -> None:
        super().process_findings(execution, findings)
        if not self.settings.execute_per_execution:
            return
        trending_cves = self._get_trending_cves()
        if not trending_cves:
            return
        for finding in findings:
            if (
                isinstance(finding, Vulnerability)
                and finding.cve is not None
                and finding.cve in trending_cves
            ):
                finding.trending = True
                finding.save(update_fields=["trending"])

    @classmethod
    def monitor(cls) -> None:
        logger.info(f"[CVE Crowd - Monitor] Cron job has started")
        trending_cves = cls()._get_trending_cves()
        if not trending_cves:
            logger.warn(f"[CVE Crowd - Monitor] No trending CVEs found")
            return
        already_trending_cves = Vulnerability.objects.filter(trending=True).all()
        already_trending_cves.exclude(cve__in=trending_cves).update(trending=False)
        Vulnerability.objects.filter(trending=False, cve__in=trending_cves).update(
            trending=True
        )
        for alert in Alert.objects.filter(
            item=AlertItem.CVE, mode=AlertMode.MONITOR, enabled=True
        ).all():
            vulnerabilities = (
                Vulnerability.objects.filter(
                    executions__task__target__project=alert.project,
                    cve__isnull=False,
                    is_fixed=False,
                    trending=True,
                )
                .exclude(
                    triage_status=TriageStatus.FALSE_POSITIVE,
                    cve__in=already_trending_cves.values("cve"),
                )
                .all()
            )
            for vulnerability in vulnerabilities:
                if alert._must_be_triggered(None, vulnerability):
                    for platform in [SMTP, Telegram]:
                        # TODO: Trigger alert notification
                        pass
        logger.info(f"[CVE Crowd - Monitor] Cron job has finished")
