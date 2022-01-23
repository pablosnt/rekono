from typing import List

from executions.models import Execution
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Finding, Host, Technology, Vulnerability)
from telegram.utils.helpers import escape_markdown
from telegram_bot.messages import findings as messages
from telegram_bot.messages.constants import DATE_FORMAT

'''Messages for execution notification.'''

EXECUTION_NOTIFICATION = '''
*{project}*

_Target_            *{target}*
_Tool_              *{tool}*
_Configuration_     {configuration}
_Status_            *{status}*
_Start_             {start}
_End_               {end}
_Executor_          {executor}

{findings}
'''


def create_telegram_message(execution: Execution, findings: List[Finding]) -> str:
    '''Create Telegram text message including execution and findings details.

    Args:
        execution (Execution): Execution to include in the message
        findings (List[Finding]): Finding list to include in the message

    Returns:
        str: Text message with execution and findings details
    '''
    text_message = ''
    finding_models = [OSINT, Host, Enumeration, Endpoint, Technology, Credential, Vulnerability, Exploit]
    for model in finding_models:                                                # For each finding model
        entities = [f for f in findings if isinstance(f, model)]                # Get findings related to current model
        if entities:                                                            # Findings found
            text_message += messages.TITLE.format(                              # Create finding name title
                icon=getattr(messages, f'{model.__name__.upper()}_ICON'),
                finding=model.__name__.upper()
            )
            for entity in entities:                                             # For each finding
                data = vars(entity)                                             # Get finding data
                data = {k: v if v else '' for k, v in data.items()}             # Clean null values from finding data
                for field in [f.__name__.lower() for f in finding_models if hasattr(entity, f.__name__.lower())]:
                    # For each potential relation with other finding type
                    # Replace related finding by its string representation
                    data[field] = getattr(entity, field).__str__()
                for finding_model, fields in [
                    (Vulnerability, ['technology', 'enumeration']),
                    (Exploit, ['vulnerability', 'technology'])
                ]:
                    # For each model with multiple findings relations, select the most relevant one
                    if isinstance(entity, finding_model):
                        for field in fields:                                    # For each relation field
                            if hasattr(entity, field) and getattr(entity, field):   # Check if field exists
                                # Add field data to the text message
                                getattr(messages, f'{field.upper()}_PARAM').format(getattr(entity, field).__str__())
                                break                                           # Only get the most relevant relation
                        break
                # Escape finding data values
                data = {k: v if not isinstance(v, str) else escape_markdown(v, version=2) for k, v in data.items()}
                # Add finding data to the text message
                text_message += getattr(messages, model.__name__.upper()).format(**data)
    # Create text message with execution details and findings message
    return EXECUTION_NOTIFICATION.format(
        project=escape_markdown(execution.task.target.project.name, version=2),
        target=escape_markdown(execution.task.target.target, version=2),
        tool=escape_markdown(execution.step.tool.name if execution.step else execution.task.tool.name, version=2),
        configuration=escape_markdown(execution.step.configuration.name if execution.step else execution.task.configuration.name, version=2),   # noqa: E501
        status=escape_markdown(execution.status, version=2),
        start=escape_markdown(execution.start.strftime(DATE_FORMAT), version=2),
        end=escape_markdown(execution.end.strftime(DATE_FORMAT), version=2),
        executor=escape_markdown(execution.task.executor.username, version=2),
        findings=text_message
    )
