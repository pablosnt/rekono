from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.update import Update
from telegram_bot.messages.selection import create_selection_message
from telegram_bot.services.security import get_chat


def show(update: Update, context: CallbackContext) -> None:
    '''Show selected items.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    chat = get_chat(update)
    if chat:
        update.message.reply_text(create_selection_message(chat), parse_mode=ParseMode.MARKDOWN_V2)


def clear(update: Update, context: CallbackContext) -> None:
    '''Clear all selected items.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    chat = get_chat(update)
    if chat:
        chat.project = None                                                     # Unselect project
        chat.target = None                                                      # Unselect target
        chat.save(update_fields=['project', 'target'])
        update.message.reply_text(create_selection_message(chat), parse_mode=ParseMode.MARKDOWN_V2)


def clear_target(update: Update, context: CallbackContext) -> None:
    '''Clear the selected target.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    chat = get_chat(update)
    if chat:
        chat.target = None                                                      # Unselect target
        chat.save(update_fields=['target'])
        update.message.reply_text(create_selection_message(chat), parse_mode=ParseMode.MARKDOWN_V2)
