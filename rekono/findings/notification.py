from typing import Any

from mail import sender
from telegram_bot import bot
from users.models import User

# TODO: Notifications refactoring


def get_parameters(execution: Any, findings: list) -> dict:
    parameters = {
        'execution': execution,
        'tool': execution.step.tool if execution.step else execution.task.tool,
        'osint': [],
        'host': [],
        'enumeration': [],
        'technology': [],
        'endpoint': [],
        'vulnerability': [],
        'credential': [],
        'exploit': [],
    }
    for finding in findings:
        parameters[finding.__class__.__name__.lower()].append(finding)
    return parameters


def send_email(user: User, execution: Any, findings: list) -> None:
    if not findings:
        return
    metadata = {
        'template': 'execution_notification.html',
        'subject': '[Rekono] Execution completed',
    }
    sender.send_html_message(
        user.email,
        metadata,
        get_parameters(execution, findings)
    )


def send_telegram_message(user: User, execution: Any, findings: list) -> None:
    if not findings:
        return
    parameters = get_parameters(execution, findings)
    bot.send_html_message(user.telegram_id, parameters)
