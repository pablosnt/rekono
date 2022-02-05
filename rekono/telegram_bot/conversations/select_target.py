from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.conversations.ask import ask_for_project, ask_for_target
from telegram_bot.messages.selection import (SELECTED_PROJECT, SELECTED_TARGET,
                                             create_selection_message)
from telegram_bot.services.projects import save_project_by_id
from telegram_bot.services.security import get_chat
from telegram_bot.services.targets import save_target_by_id

ST_SELECT_PROJECT = 0                                                           # First state: select project
ST_SELECT_TARGET = 1                                                            # Second state: select target


def target(update: Update, context: CallbackContext) -> int:
    '''Select target to be used via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if chat.project:                                                        # Project already selected
            return ask_for_target(update, chat, ST_SELECT_TARGET)               # Ask for target selection
        else:                                                                   # No selected project
            return ask_for_project(update, chat, ST_SELECT_PROJECT)             # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_project_before_target(update: Update, context: CallbackContext) -> int:
    '''Select project before target selection.

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
        return ask_for_target(update, chat, ST_SELECT_TARGET)                   # Ask for target selection
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_target(update: Update, context: CallbackContext) -> int:
    '''Select target.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    update.callback_query.answer()                                              # Empty answer
    if chat:
        target = save_target_by_id(chat, int(update.callback_query.data))       # Save selected target
        update.callback_query.answer(SELECTED_TARGET.format(target=target.target))      # Confirm selection
        update.callback_query.bot.send_message(                                 # Show selection status
            chat.chat_id,
            text=create_selection_message(chat),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    return ConversationHandler.END                                              # End conversation
