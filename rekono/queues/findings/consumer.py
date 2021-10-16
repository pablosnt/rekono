from django_rq import job
from executions.models import Execution
from findings.models import Vulnerability
from findings.enums import Severity
from integrations.nist import cve
from users.enums import Notification
from integrations.mail.executions import send_notification


@job('findings-queue')
def process_findings(execution: Execution = None, findings: list = [], domain: str = None) -> None:
    if execution:
        for finding in findings:
            setattr(finding, 'execution', execution)
            if isinstance(finding, Vulnerability) and finding.cve:
                cve_info = cve.get_information(finding.cve)
                finding.description = cve_info.get('description', '')
                finding.severity = cve_info.get('severity', Severity.MEDIUM)
                finding.reference = cve_info.get('reference', '')
            finding.save()
        if execution.task.executor.notification_preference == Notification.MAIL:
            send_notification(execution, findings, domain)
