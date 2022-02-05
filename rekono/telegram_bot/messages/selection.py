from telegram.utils.helpers import escape_markdown
from telegram_bot.models import TelegramChat

'''Messages with selected items.'''

SELECTED_PROJECT = 'Project {project} has been selected'
SELECTED_TARGET = 'Target {target} has been selected'

SELECTION = '''
*SELECTED ITEMS*

💼 _Project_   *{project}*
🎯 _Target_    *{target}*
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
        target=escape_markdown(chat.target.target if chat.target else '', version=2)        # Target details
    )
