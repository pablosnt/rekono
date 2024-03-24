import logging
from typing import List

from django_rq import job
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
from platforms.defect_dojo.integrations import DefectDojo
from platforms.hacktricks import HackTricks
from platforms.mail.notifications import SMTP
from platforms.nvd_nist import NvdNist
from platforms.telegram_app.notifications.notifications import Telegram
from rq.job import Job
from settings.models import Settings

logger = logging.getLogger()


class FindingsQueue(BaseQueue):
    name = "findings"

    def enqueue(self, execution: Execution, findings: List[Finding]) -> Job:
        job = super().enqueue(execution=execution, findings=findings)
        logger.info(
            f"[Findings] {len(findings)} findings from execution {execution.id} have been enqueued"
        )
        return job

    @staticmethod
    @job("findings")
    def consume(execution: Execution, findings: List[Finding]) -> None:
        if findings:
            for platform in [NvdNist, HackTricks, DefectDojo, SMTP, Telegram]:
                platform().process_findings(execution, findings)
        settings = Settings.objects.first()
        if settings.auto_fix_findings:
            for finding in findings:
                if finding.is_fixed:
                    finding.__class__.objects.unfix(finding)
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
                    finding_type.objects.filter(
                        executions__configuration=execution.configuration,
                        executions__task__target=execution.task.target,
                    )
                    .exclude(executions=execution)
                    .all()
                )
