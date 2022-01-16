from executions.models import Execution
from telegram_bot import messages
from tools.models import Tool


def build_execution_notification_message(parameters: dict) -> str:
    findings = ''
    for finding in [
        'OSINT', 'Host', 'Enumeration', 'Technology',
        'Endpoint', 'Vulnerability', 'Credential', 'Exploit'
    ]:
        if (
            finding.lower() not in parameters or
            (finding.lower() in parameters and not parameters[finding.lower()])
        ):
            continue
        findings = findings + messages.FINDING_TITLE.format(finding=finding.upper())
        for i in parameters[finding.lower()]:
            template = getattr(messages, f'{finding.upper()}_ITEM')
            findings = findings + template.format(**i.__dict__)
        findings += '\n'
    execution: Execution = parameters['execution']
    tool: Tool = parameters['tool']
    message = messages.EXECUTION_NOTIFICATION.format(
        project=execution.task.target.project.name,
        target=execution.task.target.target,
        task=execution.task.id,
        execution=execution.id,
        tool=tool.name,
        status=execution.status,
        start=execution.start,
        end=execution.end,
        findings=findings
    )
    return message
