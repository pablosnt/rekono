from projects.models import Project
from telegram_bot.models import TelegramChat


def save_project(chat: TelegramChat, project: Project) -> Project:
    chat.project = project
    chat.save(update_fields=['project'])
    return project


def save_project_by_id(chat: TelegramChat, project_id: int) -> Project:
    project = Project.objects.get(pk=project_id)
    return save_project(chat, project)
