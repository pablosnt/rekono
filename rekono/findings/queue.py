from typing import Optional

import django_rq
from django.core.exceptions import ValidationError
from django_rq import job
from executions.models import Execution
from findings.enums import Severity
from findings.models import Vulnerability
from findings.nist import get_cve_information
from findings.notification import send_email, send_telegram_message


def producer(execution: Execution, findings: list, rekono_address: str) -> None:
    findings_queue = django_rq.get_queue('findings-queue')
    findings_queue.enqueue(consumer, execution=execution, findings=findings, rekono_address=rekono_address)


@job('findings-queue')
def consumer(
    execution: Execution = None,
    findings: list = [],
    rekono_address: Optional[str] = None
) -> None:
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
        findings = [f for f in findings if f.id]
        users_to_notify = []
        if execution.task.executor.own_executions_notification:
            users_to_notify.append(execution.task.executor)
        users_to_notify.extend(list(execution.task.project.members.filter(
            all_executions_notification=True,
            id__ne=execution.task.executor.id
        ).all()))
        for user in users_to_notify:
            if user.email_notification:
                send_email(user, execution, findings, rekono_address)
            elif user.telegram_notification:
                send_telegram_message(user, execution, findings, rekono_address)
