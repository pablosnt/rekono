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

NTP_SELECT_PROJECT = 0                                                          # First state: select project
NTP_SELECT_TARGET = 1                                                           # Second state: select target
NTP_CREATE_TARGET_PORT = 2                                                      # Third state: create target port


def new_target_port(update: Update, context: CallbackContext) -> int:
    '''Create new target port via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if chat.target:                                                         # Target already selected
            update.message.reply_text(ASK_FOR_NEW_TARGET_PORT)                  # Ask for the new target port
            return NTP_CREATE_TARGET_PORT                                       # Go to target port creation
        elif chat.project:                                                      # Project already selected
            return ask_for_target(update, chat, NTP_SELECT_TARGET)              # Ask for target selection
        else:                                                                   # No selected target or project
            return ask_for_project(update, chat, NTP_SELECT_PROJECT)            # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_project_for_new_target_port(update: Update, context: CallbackContext) -> int:
    '''Select project before new target port creation.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        project = save_project_by_id(chat, int(update.callback_query.data))     # Save selected project
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))     # Confirm selection
        return ask_for_target(update, chat, NTP_SELECT_TARGET)                  # Ask for target selection
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_target_for_new_target_port(update: Update, context: CallbackContext) -> int:
    '''Select target before new target port creation.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        target = save_target_by_id(chat, int(update.callback_query.data))       # Save selected target
        update.callback_query.answer(SELECTED_TARGET.format(target=target.target))      # Confirm selection
        # Ask for the new target port
        update.callback_query.bot.send_message(chat.chat_id, text=ASK_FOR_NEW_TARGET_PORT)
        return NTP_CREATE_TARGET_PORT                                           # Go to target port creation
    update.callback_query.answer()
    return ConversationHandler.END


def create_target_port(update: Update, context: CallbackContext) -> int:
    '''Create new target port.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if update.message.text == '/cancel':                                    # Check if cancellation is requested
            return cancel(update, context)                                      # Cancel operation
        try:
            port = int(update.message.text)                                     # Check if port is a valid number
        except ValueError:
            update.message.reply_text(INVALID_TARGET_PORT)                      # Invalid target port
            update.message.reply_text(ASK_FOR_NEW_TARGET_PORT)                  # Re-ask for the new target port
            return NTP_CREATE_TARGET_PORT                                       # Repeat the current state
        # Prepare target port data
        serializer = TargetPortSerializer(data={'target': chat.target.id, 'port': port})
        if serializer.is_valid():                                               # Target port is valid
            target_port = serializer.save()                                     # Create target port
            update.message.reply_text(                                          # Confirm target port creation
                NEW_TARGET_PORT.format(
                    port=escape_markdown(str(target_port.port), version=2),
                    target=escape_markdown(target_port.target.target, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:                                                                   # Invalid target port data
            # Send error details
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET_PORT)                  # Re-ask for the new target port
            return NTP_CREATE_TARGET_PORT                                       # Repeat the current state
    return ConversationHandler.END                                              # End conversation
