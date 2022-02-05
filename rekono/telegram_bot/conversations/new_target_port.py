from targets.serializers import TargetPortSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.conversations.ask import ask_for_project, ask_for_target
from telegram_bot.conversations.cancel import cancel
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.selection import SELECTED_PROJECT, SELECTED_TARGET
from telegram_bot.messages.targets import (ASK_FOR_NEW_TARGET_PORT,
                                           INVALID_TARGET_PORT,
                                           NEW_TARGET_PORT)
from telegram_bot.services.projects import save_project_by_id
from telegram_bot.services.security import get_chat
from telegram_bot.services.targets import save_target_by_id

NTP_SELECT_PROJECT = 0
NTP_SELECT_TARGET = 1
NTP_CREATE_TARGET_PORT = 2


def new_target_port(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        if chat.target:
            update.message.reply_text(ASK_FOR_NEW_TARGET_PORT)
            return NTP_CREATE_TARGET_PORT
        elif chat.project:
            return ask_for_target(update, chat, NTP_SELECT_TARGET)
        else:
            return ask_for_project(update, chat, NTP_SELECT_PROJECT)
    return ConversationHandler.END


def select_project_for_new_target_port(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        project = save_project_by_id(chat, int(update.callback_query.data))
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))
        return ask_for_target(update, chat, NTP_SELECT_TARGET)
    update.callback_query.answer()
    return ConversationHandler.END


def select_target_for_new_target_port(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        target = save_target_by_id(chat, int(update.callback_query.data))
        update.callback_query.answer(SELECTED_TARGET.format(target=target.target))
        update.callback_query.bot.send_message(chat.chat_id, text=ASK_FOR_NEW_TARGET_PORT)
        return NTP_CREATE_TARGET_PORT
    update.callback_query.answer()
    return ConversationHandler.END


def create_target_port(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        if update.message.text == '/cancel':
            return cancel(update, context)
        try:
            port = int(update.message.text)
        except ValueError:
            update.message.reply_text(INVALID_TARGET_PORT)
            update.message.reply_text(ASK_FOR_NEW_TARGET_PORT)
            return NTP_CREATE_TARGET_PORT
        serializer = TargetPortSerializer(data={'target': chat.target.id, 'port': port})
        if serializer.is_valid():
            target_port = serializer.save()
            update.message.reply_text(
                NEW_TARGET_PORT.format(
                    target=escape_markdown(target_port.target.target, version=2),
                    port=escape_markdown(str(target_port.port), version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET_PORT)
            return NTP_CREATE_TARGET_PORT
    return ConversationHandler.END
