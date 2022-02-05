from targets.serializers import TargetEndpointSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.conversations.ask import (ask_for_project, ask_for_target,
                                            ask_for_target_port)
from telegram_bot.conversations.cancel import cancel
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.selection import SELECTED_PROJECT, SELECTED_TARGET
from telegram_bot.messages.targets import (ASK_FOR_NEW_TARGET_ENDPOINT,
                                           NEW_TARGET_ENDPOINT)
from telegram_bot.services.projects import save_project_by_id
from telegram_bot.services.security import get_chat
from telegram_bot.services.targets import (save_target_by_id,
                                           save_target_port_by_id)

NTE_SELECT_PROJECT = 0
NTE_SELECT_TARGET = 1
NTE_SELECT_TARGET_PORT = 2
NTE_CREATE_TARGET_ENDPOINT = 3


def new_target_endpoint(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        if chat.target:
            return ask_for_target_port(update, chat, NTE_SELECT_TARGET_PORT)
        elif chat.project:
            return ask_for_target(update, chat, NTE_SELECT_TARGET)
        else:
            return ask_for_project(update, chat, NTE_SELECT_PROJECT)
    return ConversationHandler.END


def select_project_for_new_target_endpoint(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        project = save_project_by_id(chat, int(update.callback_query.data))
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))
        return ask_for_target(update, chat, NTE_SELECT_TARGET)
    update.callback_query.answer()
    return ConversationHandler.END


def select_target_for_new_target_endpoint(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        target = save_target_by_id(chat, int(update.callback_query.data))
        update.callback_query.answer(SELECTED_TARGET.format(target=target.target))
        return ask_for_target_port(update, chat, NTE_SELECT_TARGET_PORT)
    update.callback_query.answer()
    return ConversationHandler.END


def select_target_port_for_new_target_endpoint(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        save_target_port_by_id(chat, int(update.callback_query.data))
        update.callback_query.bot.send_message(chat.chat_id, text=ASK_FOR_NEW_TARGET_ENDPOINT)
        return NTE_CREATE_TARGET_ENDPOINT
    update.callback_query.answer()
    return ConversationHandler.END


def create_target_endpoint(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        if update.message.text == '/cancel':
            return cancel(update, context)
        serializer = TargetEndpointSerializer(data={'target_port': chat.target_port.id, 'endpoint': update.message.text})
        if serializer.is_valid():
            target_endpoint = serializer.save()
            update.message.reply_text(
                NEW_TARGET_ENDPOINT.format(
                    endpoint=escape_markdown(target_endpoint.endpoint, version=2),
                    target=escape_markdown(target_endpoint.target_port.target.target, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            input(serializer.errors)
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET_ENDPOINT)
            return NTE_CREATE_TARGET_ENDPOINT
    return ConversationHandler.END
