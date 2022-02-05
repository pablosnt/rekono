from email import message
from typing import List

from projects.models import Project
from targets.models import Target
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.update import Update
from telegram_bot.messages.selection import (ASK_FOR_PROJECT, ASK_FOR_TARGET,
                                             NO_PROJECTS, NO_TARGETS)
from telegram_bot.models import TelegramChat


def send_message(update: Update, chat: TelegramChat, text: str) -> None:
    if hasattr(update, 'message') and getattr(update, 'message'):
        update.message.reply_text(text)
    else:
        update.callback_query.bot.send_message(chat.chat_id, text=text)


def send_options(update: Update, chat: TelegramChat, text: str, keyboard: List[List[InlineKeyboardButton]]) -> None:
    if hasattr(update, 'message') and getattr(update, 'message'):
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.callback_query.bot.send_message(chat.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def ask_for_project(update: Update, chat: TelegramChat, next_stage: int) -> int:
    projects = Project.objects.filter(members=chat.user).order_by('name').all()
    if not projects:
        send_message(update, chat, NO_PROJECTS)
        return ConversationHandler.END
    else:
        keyboard = [[InlineKeyboardButton(p.name, callback_data=p.id) for p in projects]]
        send_options(update, chat, ASK_FOR_PROJECT, keyboard)
        return next_stage


def ask_for_target(update: Update, chat: TelegramChat, next_stage: int) -> int:
    targets = Target.objects.filter(project=chat.project).order_by('target').all()
    if not targets:
        send_message(update, chat, NO_TARGETS)
        return ConversationHandler.END
    else:
        keyboard = [[InlineKeyboardButton(t.target, callback_data=t.id) for t in targets]]
        send_options(update, chat, ASK_FOR_TARGET, keyboard)
        return next_stage
