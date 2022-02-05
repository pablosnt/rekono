from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.conversations.ask import ask_for_process
from telegram_bot.messages.selection import (SELECTED_PROCESS,
                                             create_selection_message)
from telegram_bot.services.processes import save_process_by_id
from telegram_bot.services.security import get_chat

SP_SELECT_PROCESS = 0                                                           # First state: select process


def process(update: Update, context: CallbackContext) -> int:
    '''Select process to be used via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        return ask_for_process(update, chat, SP_SELECT_PROCESS)                 # Ask for process selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_process(update: Update, context: CallbackContext) -> int:
    '''Select process.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    update.callback_query.answer()                                              # Empty answer
    if chat:
        process = save_process_by_id(chat, int(update.callback_query.data))     # Save selected process
        update.callback_query.answer(SELECTED_PROCESS.format(process=process.name))     # Confirm selection
        update.callback_query.bot.send_message(                                 # Show selection status
            chat.chat_id,
            text=create_selection_message(chat),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    return ConversationHandler.END                                              # End conversation
