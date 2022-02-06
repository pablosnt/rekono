from typing import List

from processes.models import Process
from projects.models import Project
from targets.models import Target, TargetPort
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import (CONFIGURATION, INTENSITY, PROCESS, PROJECT,
                                  STATES, TARGET, TARGET_PORT, TOOL)
from telegram_bot.messages.selection import (SELECTED_CONFIGURATION,
                                             SELECTED_INTENSITY,
                                             SELECTED_PROCESS,
                                             SELECTED_PROJECT, SELECTED_TARGET,
                                             SELECTED_TARGET_PORT,
                                             SELECTED_TOOL, SELECTION)
from telegram_bot.models import TelegramChat
from telegram_bot.security import get_chat
from tools.models import Configuration, Tool


def next_state(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    if STATES in context.chat_data and context.chat_data[STATES]:
        state, action = context.chat_data[STATES][0]
        context.chat_data[STATES] = context.chat_data[STATES][1:]
        if action:
            if isinstance(action, str):
                update.callback_query.bot.send_message(chat.chat_id, text=action)
            elif callable(action):
                return action(update, context, chat)
        return state
    return ConversationHandler.END                                              # End conversation


def select_project(update: Update, context: CallbackContext) -> int:
    '''Select project.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        project = Project.objects.get(pk=int(update.callback_query.data))
        context.chat_data[PROJECT] = project                                    # Save selected project
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))     # Confirm selection
        next = next_state(update, context, chat)
        if next == ConversationHandler.END:
            update.callback_query.bot.send_message(
                chat.chat_id,
                text=SELECTION.format(project=escape_markdown(context.chat_data[PROJECT].name, version=2)),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        return next
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_target(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        target = Target.objects.get(pk=int(update.callback_query.data))
        context.chat_data[TARGET] = target                                      # Save selected project
        update.callback_query.answer(SELECTED_TARGET.format(target=target.target))     # Confirm selection
        return next_state(update, context, chat)
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_target_port(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        target_port = TargetPort.objects.get(pk=int(update.callback_query.data))
        context.chat_data[TARGET_PORT] = target_port                                      # Save selected project
        update.callback_query.answer(SELECTED_TARGET_PORT.format(port=target_port.port))     # Confirm selection
        return next_state(update, context, chat)
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_tool(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        tool = Tool.objects.get(pk=int(update.callback_query.data))
        context.chat_data[TOOL] = tool                                      # Save selected project
        update.callback_query.answer(SELECTED_TOOL.format(tool=tool.name))     # Confirm selection
        return next_state(update, context, chat)
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_process(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        process = Process.objects.get(pk=int(update.callback_query.data))
        context.chat_data[PROCESS] = process                                      # Save selected project
        update.callback_query.answer(SELECTED_PROCESS.format(process=process.name))     # Confirm selection
        return next_state(update, context, chat)
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_configuration(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        configuration = Configuration.objects.get(pk=int(update.callback_query.data))
        context.chat_data[CONFIGURATION] = configuration                                      # Save selected project
        update.callback_query.answer(SELECTED_CONFIGURATION.format(configuration=configuration.name))     # Confirm selection
        return next_state(update, context, chat)
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_intensity(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        context.chat_data[INTENSITY] = update.callback_query.data.upper()                                      # Save selected project
        update.callback_query.answer(SELECTED_INTENSITY.format(intensity=update.callback_query.data.capitalize()))     # Confirm selection
        return next_state(update, context, chat)
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # End conversation


def clear(context: CallbackContext, keys: List[str]) -> None:
    for key in keys:
        if key in context.chat_data:
            context.chat_data.pop(key)
