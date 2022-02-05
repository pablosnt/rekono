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

NTE_SELECT_PROJECT = 0                                                          # First state: select project
NTE_SELECT_TARGET = 1                                                           # Second state: select target
NTE_SELECT_TARGET_PORT = 2                                                      # Third state: select target port
NTE_CREATE_TARGET_ENDPOINT = 3                                                  # Fourth state: create target endpoint


def new_target_endpoint(update: Update, context: CallbackContext) -> int:
    '''Create new target endpoint via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if chat.target:                                                         # Target already selected
            return ask_for_target_port(update, chat, NTE_SELECT_TARGET_PORT)    # Ask for target port selection
        elif chat.project:                                                      # Project already selected
            return ask_for_target(update, chat, NTE_SELECT_TARGET)              # Ask for target selection
        else:                                                                   # No selected target or project
            return ask_for_project(update, chat, NTE_SELECT_PROJECT)            # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_project_for_new_target_endpoint(update: Update, context: CallbackContext) -> int:
    '''Select project before new target endpoint creation.

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
        return ask_for_target(update, chat, NTE_SELECT_TARGET)                  # Ask for target selection
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_target_for_new_target_endpoint(update: Update, context: CallbackContext) -> int:
    '''Select target before new target endpoint creation.

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
        return ask_for_target_port(update, chat, NTE_SELECT_TARGET_PORT)        # Ask for target port selection
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_target_port_for_new_target_endpoint(update: Update, context: CallbackContext) -> int:
    '''Select target port before new target endpoint creation.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        save_target_port_by_id(chat, int(update.callback_query.data))           # Save selected target port
        # Ask for new target endpoint
        update.callback_query.bot.send_message(chat.chat_id, text=ASK_FOR_NEW_TARGET_ENDPOINT)
        return NTE_CREATE_TARGET_ENDPOINT                                       # Go to target endpoint creation
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # Unauthorized: end conversation


def create_target_endpoint(update: Update, context: CallbackContext) -> int:
    '''Create new target endpoint.

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
        serializer = TargetEndpointSerializer(                                  # Prepare target endpoint data
            data={'target_port': chat.target_port.id, 'endpoint': update.message.text}
        )
        if serializer.is_valid():                                               # Target endpoint is valid
            target_endpoint = serializer.save()                                 # Create target endpoint
            update.message.reply_text(                                          # Confirm target endpoint creation
                NEW_TARGET_ENDPOINT.format(
                    endpoint=escape_markdown(target_endpoint.endpoint, version=2),
                    target=escape_markdown(target_endpoint.target_port.target.target, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:                                                                   # Invalid target endpoint data
            # Send error details
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET_ENDPOINT)              # Re-ask for the new target endpoint
            return NTE_CREATE_TARGET_ENDPOINT                                   # Repeat the current state
    return ConversationHandler.END                                              # End conversation
