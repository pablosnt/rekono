from telegram.utils.helpers import escape_markdown
from telegram_bot.models import TelegramChat

'''Messages with selected items.'''

SELECTED_PROJECT = 'Project {project} has been selected'
SELECTED_TARGET = 'Target {target} has been selected'
SELECTED_PROCESS = 'Process {process} has been selected'
SELECTED_TOOL = 'Tool {tool} has been selected'

SELECTION = '''
*SELECTED ITEMS*

💼 _Project_   *{project}*
🎯 _Target_    *{target}*
⛓ _Process_   *{process}*
🛠 _Tool_      *{tool}*
'''


def create_selection_message(chat: TelegramChat) -> str:
    '''Create text message with the selected items details.

    Args:
        chat (TelegramChat): Telegram chat entity

    Returns:
        str: Text message
    '''
    return SELECTION.format(
        project=escape_markdown(chat.project.name if chat.project else '', version=2),      # Project details
        target=escape_markdown(chat.target.target if chat.target else '', version=2),       # Target details
        process=escape_markdown(chat.process.name if chat.process else '', version=2),      # Process details
        tool=escape_markdown(chat.tool.name if chat.tool else '', version=2)    # Tool details
    )
