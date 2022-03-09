from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import PROJECT
from telegram_bot.messages.selection import (CLEAR_SELECTION, NO_SELECTION,
                                             SELECTION)
from telegram_bot.security import get_chat


def show(update: Update, context: CallbackContext) -> None:
    '''Show selected project.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and update.effective_message:
        if context.chat_data and PROJECT in context.chat_data:      # Selected project
            update.effective_message.reply_text(
                SELECTION.format(project=escape_markdown(context.chat_data[PROJECT].name, version=2)),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:                                                                   # No selected project
            update.effective_message.reply_text(NO_SELECTION)


def clear(update: Update, context: CallbackContext) -> None:
    '''Unselect selected project.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and update.effective_message:
        if context.chat_data and PROJECT in context.chat_data:                  # Selected project
            context.chat_data.pop(PROJECT)                                      # Unselect project
        update.effective_message.reply_text(CLEAR_SELECTION)
