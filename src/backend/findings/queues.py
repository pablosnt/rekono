import logging
from typing import Any, List

from django_rq import job
from executions.models import Execution
from findings.models import Finding
from framework.queues import BaseQueue
from rq.job import Job

logger = logging.getLogger()


class FindingsQueue(BaseQueue):
    def __init__(self) -> None:
        super().__init__("findings-queue")

    def enqueue(self, execution: Execution, findings: List[Finding]) -> Job:
        job = super().enqueue(execution=execution, findings=findings)
        logger.info(
            f"[Findings] {len(findings)} findings from execution {execution.id} have been enqueued"
        )
        return job

    @job("findings-queue")
    def consume(self, execution: Execution, findings: List[Finding]) -> List[Finding]:
        # TODO: Requires the implementation of new integrations
        pass
