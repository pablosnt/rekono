from telegram.utils.helpers import escape_markdown
from telegram_bot.models import TelegramChat

ASK_FOR_PROJECT = 'Choose one project'
SELECTED_PROJECT = 'Project {project} has been selected'
NO_PROJECTS = 'You have no projects. Go to Rekono to create one or ask your administrator for assign you to existing one'

ASK_FOR_TARGET = 'Choose one target'
SELECTED_TARGET = 'Target {target} has been selected'
NO_TARGETS = 'There are no targets in this project. Use the command /newtarget'

SELECTION = '''
*SELECTED ITEMS*

💼 _Project_   *{project}*
🎯 _Target_    *{target}*
'''

def create_selection_message(chat: TelegramChat) -> str:
    return SELECTION.format(
        project=escape_markdown(chat.project.name if chat.project else '', version=2),
        target=escape_markdown(chat.target.target if chat.target else '', version=2)
    )
