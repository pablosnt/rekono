import django_rq
from django_rq import job
from executions.models import Execution
from findings.models import Vulnerability
from findings.enums import Severity
from findings.nist import get_cve_information
from users.enums import Notification
from findings.mail import send_notification


def producer(execution: Execution, findings: list, domain: str) -> None:
    findings_queue = django_rq.get_queue('findings-queue')
    findings_queue.enqueue(
        consumer,
        execution=execution,
        findings=findings,
        domain=domain
    )


@job('findings-queue')
def consumer(execution: Execution = None, findings: list = [], domain: str = None) -> None:
    if execution:
        for finding in findings:
            setattr(finding, 'execution', execution)
            if isinstance(finding, Vulnerability) and finding.cve:
                cve_info = get_cve_information(finding.cve)
                finding.description = cve_info.get('description', '')
                finding.severity = cve_info.get('severity', Severity.MEDIUM)
                finding.reference = cve_info.get('reference', '')
            finding.save()
        if execution.task.executor.notification_preference == Notification.MAIL:
            send_notification(execution, findings, domain)
