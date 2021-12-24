from typing import Any

from mail import sender
from telegram_bot import bot


def get_parameters(execution: Any, findings: list, rekono_address: str) -> dict:
    parameters = {
        'rekono_address': rekono_address if rekono_address else '127.0.0.1:8000',
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


def send_email(execution: Any, findings: list, rekono_address: str) -> None:
    if not findings:
        return
    metadata = {
        'template': 'execution_notification.html',
        'subject': '[Rekono] Execution completed',
    }
    sender.send_html_message(
        execution.task.executor.email,
        metadata,
        get_parameters(execution, findings, rekono_address)
    )


def send_telegram_message(execution: Any, findings: list, rekono_address: str) -> None:
    if not findings:
        return
    parameters = get_parameters(execution, findings, rekono_address)
    bot.send_html_message(execution.task.executor.telegram_id, parameters)
