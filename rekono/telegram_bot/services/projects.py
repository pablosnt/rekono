from projects.models import Project
from telegram_bot.models import TelegramChat


def save_project_by_id(chat: TelegramChat, project_id: int) -> Project:
    '''Save project as selected for one Telegram chat.

    Args:
        chat (TelegramChat): Telegram chat entity
        project_id (int): Project Id to select

    Returns:
        Project: Selected project entity
    '''
    project = Project.objects.get(pk=project_id)                                # Get project by Id
    chat.project = project                                                      # Select project
    chat.save(update_fields=['project'])
    return project
