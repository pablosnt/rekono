from typing import List

import django_rq
from django_rq import job
from executions.models import Execution
from findings.models import Finding, Vulnerability
from findings.notification import send_email, send_telegram_message
from findings.nvd_nist import NvdNist
from users.enums import Notification


def producer(execution: Execution, findings: List[Finding]) -> None:
    '''Enqueue a list of findings in the findings queue.

    Args:
        execution (Execution): Execution where the findings are discovered
        findings (List[Finding]): Findings list to process
    '''
    findings_queue = django_rq.get_queue('findings-queue')                      # Get findings queue
    findings_queue.enqueue(consumer, execution=execution, findings=findings)    # Enqueue findings list


@job('findings-queue')
def consumer(execution: Execution = None, findings: List[Finding] = []) -> None:
    '''Consume jobs from findings queue and process them.

    Args:
        execution (Execution, optional): Execution where the findings are discovered. Defaults to None.
        findings (List[Finding], optional): Findings list to process. Defaults to [].
    '''
    if execution:
        for finding in findings:                                                # For each finding
            if isinstance(finding, Vulnerability) and finding.cve:              # If it's a vulnerability with CVE
                nn_client = NvdNist(finding.cve)                                # NVD NIST request to get information
                # Update vulnerability fields with the NIST information
                finding.description = nn_client.description
                finding.severity = nn_client.severity
                finding.cwe = nn_client.cwe
                finding.reference = nn_client.reference
                finding.save(update_fields=['description', 'severity', 'cwe', 'reference'])
        users_to_notify = []
        # Executor with enabled own executions notification
        if execution.task.executor.notification_scope == Notification.OWN_EXECUTIONS:
            users_to_notify.append(execution.task.executor)                     # Save executor user in the notify list
        # Search project members with enabled all executions notification
        search_members = execution.task.target.project.members.filter(notification_scope=Notification.ALL_EXECUTIONS).all()     # noqa: E501
        users_to_notify.extend(list(search_members))                            # Save members in the notify list
        for user in users_to_notify:                                            # For each user to be notified
            if user.email_notification:
                send_email(user, execution, findings)                           # Email notification
            elif user.telegram_notification:
                send_telegram_message(user, execution, findings)                # Telegram notification
