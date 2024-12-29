import logging

from django_rq import job
from executions.enums import Status
from executions.models import Execution
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Finding,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)
from framework.queues import BaseQueue
from platforms.cvecrowd.integrations import CveCrowd
from platforms.defectdojo.integrations import DefectDojo
from platforms.hacktricks import HackTricks
from platforms.mail.notifications import SMTP
from platforms.nvdnist.integrations import NvdNist
from platforms.telegram_app.notifications.notifications import Telegram
from rq.job import Job
from settings.models import Settings

logger = logging.getLogger()


class FindingsQueue(BaseQueue):
    name = "findings"

    def enqueue(self, execution: Execution, findings: list[Finding]) -> Job:
        job = super().enqueue(execution=execution, findings=findings)
        logger.info(
            f"[Findings] {len(findings)} findings from execution {execution.id} have been enqueued"
        )
        return job

    @staticmethod
    @job("findings")
    def consume(execution: Execution, findings: list[Finding]) -> None:
        settings = Settings.objects.first()
        if findings:
            notifications = [SMTP(), Telegram()]
            for platform in [
                NvdNist(),
                HackTricks(),
                CveCrowd(),
                DefectDojo(),
            ] + notifications:
                platform.process_findings(execution, findings)
            for finding in findings:
                if settings.auto_fix_findings and finding.is_fixed:
                    finding.__class__.objects.remove_fix(finding)
                for alert in (
                    execution.task.target.project.alerts.filter(enabled=True)
                    .order_by("-item")
                    .all()
                ):
                    if alert.must_be_triggered(execution, finding):
                        for platform in notifications:
                            platform.process_alert(alert, finding)
                        break
        if settings.auto_fix_findings:
            same_executions = Execution.objects.filter(
                hash=execution.hash, status=Status.COMPLETED
            )
            for finding_type in [
                OSINT,
                Host,
                Port,
                Path,
                Technology,
                Credential,
                Vulnerability,
                Exploit,
            ]:
                finding_type.objects.fix(
                    finding_type.objects.exclude(executions__id=execution.id)
                    .filter(executions__in=same_executions)
                    .all()
                )
