from typing import Any

from integrations.mail.utils import send_html_message


metadata = {
    'execution': {
        'template': 'execution_notification.html',
        'subject': '[Rekono] Execution completed',
    }
}


def send_notification(execution: Any, findings: list, domain: str) -> None:
    if not findings:
        return
    parameters = {
        'domain': domain,
        'execution': execution,
        'tool': execution.step.tool if execution.step else execution.task.tool,
        'osint': [],
        'host': [],
        'enumeration': [],
        'technology': [],
        'httpendpoint': [],
        'vulnerability': [],
        'exploit': [],
    }
    for finding in findings:
        parameters[finding.__class__.__name__.lower()].append(finding)
    send_html_message(execution.task.executor.email, metadata.get('execution'), parameters)
