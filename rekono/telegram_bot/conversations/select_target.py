from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.conversations.ask import ask_for_project, ask_for_target
from telegram_bot.messages.selection import (SELECTED_PROJECT, SELECTED_TARGET,
                                             create_selection_message)
from telegram_bot.services.projects import save_project_by_id
from telegram_bot.services.security import get_chat
from telegram_bot.services.targets import save_target_by_id

ST_SELECT_PROJECT = 0
ST_SELECT_TARGET = 1


def target(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        if chat.project:
            return ask_for_target(update, chat, ST_SELECT_TARGET)
        else:
            return ask_for_project(update, chat, ST_SELECT_PROJECT)
    return ConversationHandler.END


def select_project_before_target(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        project = save_project_by_id(chat, int(update.callback_query.data))
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))
        return ask_for_target(update, chat, ST_SELECT_TARGET)
    update.callback_query.answer()
    return ConversationHandler.END


def select_target(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        target = save_target_by_id(chat, int(update.callback_query.data))
        update.callback_query.answer(SELECTED_TARGET.format(target=target.target))
        update.callback_query.bot.send_message(chat.chat_id, text=create_selection_message(chat), parse_mode=ParseMode.MARKDOWN_V2)
    update.callback_query.answer()
    return ConversationHandler.END
