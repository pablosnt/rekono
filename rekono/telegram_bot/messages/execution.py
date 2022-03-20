from typing import List

from executions.models import Execution
from findings.models import (OSINT, Credential, Endpoint, Port, Exploit,
                             Finding, Host, Technology, Vulnerability)
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import (CONFIGURATION, INTENSITY, PROCESS, PROJECT,
                                  TARGET, TOOL)
from telegram_bot.messages import findings as messages
from telegram_bot.messages.constants import DATE_FORMAT

'''Messages related to executions.'''

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

EXECUTION_CONFIRMATION = '''
The following execution will be launched:

💼 _Project_   *{project}*
🎯 _Target_    *{target}*
{execution_item}
🔊 _Intensity_ *{intensity}*

Are you sure?
'''

PROCESS_CONFIRMATION = '⛓ _Process_   *{process}*'

TOOL_CONFIRMATION = '''🛠 _Tool_      *{tool}*
📄 _Configuration_  *{configuration}*'''

EXECUTION_LAUNCHED = '✅ Task {id} created successfully!'


def notification_message(execution: Execution, findings: List[Finding]) -> str:
    '''Create text message including execution and findings details.

    Args:
        execution (Execution): Execution to include in the message
        findings (List[Finding]): Finding list to include in the message

    Returns:
        str: Text message with execution and findings details
    '''
    text_message = ''
    finding_models = [OSINT, Host, Port, Endpoint, Technology, Credential, Vulnerability, Exploit]
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
                    (Vulnerability, ['technology', 'port']),
                    (Exploit, ['vulnerability', 'technology'])
                ]:
                    # For each model with multiple findings relations, select the most relevant one
                    if isinstance(entity, finding_model):
                        for field in fields:                                    # For each relation field
                            if hasattr(entity, field) and getattr(entity, field):   # Check if field exists
                                # Add field data to the text message
                                relation_text = {field: getattr(entity, field).__str__()}
                                data[field] = getattr(messages, f'{field.upper()}_PARAM').format(**relation_text)
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


def confirmation_message(context: CallbackContext) -> str:
    '''Create text message to ask user for confirmation before start execution.

    Args:
        context (CallbackContext): Telegram Bot context

    Returns:
        str: Text message for execution confirmation
    '''
    execution_item = ''
    if context.chat_data:
        if TOOL in context.chat_data:                                           # Tool execution
            execution_item = TOOL_CONFIRMATION.format(
                tool=escape_markdown(context.chat_data[TOOL].name, version=2),
                configuration=escape_markdown(context.chat_data[CONFIGURATION].name, version=2)
            )
        elif PROCESS in context.chat_data:                                      # Process execution
            execution_item = PROCESS_CONFIRMATION.format(
                process=escape_markdown(context.chat_data[PROCESS].name, version=2)
            )
    return EXECUTION_CONFIRMATION.format(                                       # Create confirmation message
        project=escape_markdown(context.chat_data[PROJECT].name, version=2),
        target=escape_markdown(context.chat_data[TARGET].target, version=2),
        execution_item=execution_item,
        intensity=context.chat_data[INTENSITY].capitalize()
    )
