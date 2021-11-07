import django_rq
from django.core.exceptions import ValidationError
from django_rq import job
from executions.models import Execution
from findings.enums import Severity
from findings.models import Vulnerability
from findings.nist import get_cve_information
from findings.notification import send_email, send_telegram_message
from users.enums import Notification


def producer(execution: Execution, findings: list, domain: str) -> None:
    findings_queue = django_rq.get_queue('findings-queue')
    findings_queue.enqueue(consumer, execution=execution, findings=findings, domain=domain)


@job('findings-queue')
def consumer(execution: Execution = None, findings: list = [], domain: str = None) -> None:
    if execution:
        for finding in findings:
            if isinstance(finding, Vulnerability) and finding.cve:
                cve_info = get_cve_information(finding.cve)
                finding.description = cve_info.get('description', '')
                finding.severity = cve_info.get('severity', Severity.MEDIUM)
                finding.reference = cve_info.get('reference', '')
            try:
                finding.set_execution(execution)
                finding.save()
            except ValidationError:
                finding.delete()
        if execution.task.executor.notification_preference == Notification.EMAIL:
            send_email(execution, [f for f in findings if f.id], domain)
        elif (
            execution.task.executor.notification_preference == Notification.TELEGRAM
            and execution.task.executor.telegram_id
        ):
            send_telegram_message(execution, [f for f in findings if f.id], domain)
