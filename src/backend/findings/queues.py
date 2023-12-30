import logging
from typing import List

from django_rq import job
from executions.models import Execution
from findings.models import Finding
from framework.queues import BaseQueue
from platforms.defect_dojo.integrations import DefectDojo
from platforms.mail.notifications import SMTP
from platforms.nvd_nist import NvdNist
from platforms.telegram_app.notifications.notifications import Telegram
from rq.job import Job

logger = logging.getLogger()


class FindingsQueue(BaseQueue):
    name = "findings-queue"

    def enqueue(self, execution: Execution, findings: List[Finding]) -> Job:
        job = super().enqueue(execution=execution, findings=findings)
        logger.info(
            f"[Findings] {len(findings)} findings from execution {execution.id} have been enqueued"
        )
        return job

    @staticmethod
    @job("findings-queue")
    def consume(execution: Execution, findings: List[Finding]) -> None:
        if findings:
            for platform in [NvdNist, DefectDojo, SMTP, Telegram]:
                platform().process_findings(execution, findings)
