from typing import Optional

import django_rq
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_rq import job
from executions.models import Execution
from findings.enums import Severity
from findings.models import Vulnerability
from findings.nist import get_cve_information
from findings.notification import send_email, send_telegram_message
from users.enums import Notification


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
                finding.save()
        #     try:
        #         finding.set_execution(execution)
        #         finding.save()
        #     except ValidationError as e:
        #         print(e)
        #         finding.delete()
        # findings = [f for f in findings if f.id]
        users_to_notify = []
        if execution.task.executor.notification_scope == Notification.OWN_EXECUTIONS:
            users_to_notify.append(execution.task.executor)
        search_members = execution.task.target.project.members.filter(
            ~Q(id=execution.task.executor.id) and Q(notification_scope=Notification.ALL_EXECUTIONS)
        ).all()
        users_to_notify.extend(list(search_members))
        for user in users_to_notify:
            if user.email_notification:
                send_email(user, execution, findings, rekono_address)
            elif user.telegram_notification:
                send_telegram_message(user, execution, findings, rekono_address)
