from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.conversations.ask import ask_for_project
from telegram_bot.messages.selection import (SELECTED_PROJECT,
                                             create_selection_message)
from telegram_bot.services.projects import save_project_by_id
from telegram_bot.services.security import get_chat

SP_SELECT_PROJECT = 0                                                           # First state: select project


def project(update: Update, context: CallbackContext) -> int:
    '''Select project to be used via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        return ask_for_project(update, chat, SP_SELECT_PROJECT)                 # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_project(update: Update, context: CallbackContext) -> int:
    '''Select project.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    update.callback_query.answer()                                              # Empty answer
    if chat:
        project = save_project_by_id(chat, int(update.callback_query.data))     # Save selected project
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))     # Confirm selection
        update.callback_query.bot.send_message(                                 # Show selection status
            chat.chat_id,
            text=create_selection_message(chat),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    return ConversationHandler.END                                              # End conversation
