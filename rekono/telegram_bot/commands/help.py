from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.update import Update
from telegram_bot.messages.help import (UNAUTH_HELP, get_help_message,
                                        get_reader_help_message)
from telegram_bot.models import TelegramChat
from telegram_bot.security import check_auditor


def help(update: Update, context: CallbackContext) -> None:
    '''Get Telegram Bot help message.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    if update.effective_chat and update.effective_message:
        chat = TelegramChat.objects.filter(chat_id=update.effective_chat.id, user__is_active=True).first()
        if not chat or not chat.user:                                           # Unlinked Telegram chat
            update.effective_message.reply_text(UNAUTH_HELP, parse_mode=ParseMode.MARKDOWN_V2)
        elif check_auditor(chat):                                               # Chat linked to auditor account
            update.effective_message.reply_text(get_help_message(), parse_mode=ParseMode.MARKDOWN_V2)
        else:                                                                   # Chat linked to reader account
            update.effective_message.reply_text(get_reader_help_message(), parse_mode=ParseMode.MARKDOWN_V2)
