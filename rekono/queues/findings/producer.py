import django_rq
from executions.models import Execution
from queues.findings import consumer


def process_findings(execution: Execution, findings: list) -> None:
    findings_queue = django_rq.get_queue('findings-queue')
    findings_queue.enqueue(consumer.process_findings, execution=execution, findings=findings)