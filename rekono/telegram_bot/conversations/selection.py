from projects.models import Project
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.update import Update
from telegram_bot.messages.selection import ASK_FOR_PROJECT, NO_PROJECTS
from telegram_bot.models import TelegramChat


def ask_for_project(update: Update, chat: TelegramChat, next_stage: int) -> int:
    projects = Project.objects.filter(members=chat.user).order_by('name').all()
    if not projects:
        update.message.reply_text(NO_PROJECTS)
    else:
        keyboard = [[InlineKeyboardButton(p.name, callback_data=p.id) for p in projects]]
        update.message.reply_text(ASK_FOR_PROJECT, reply_markup=InlineKeyboardMarkup(keyboard))
        return next_stage
