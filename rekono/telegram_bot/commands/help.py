from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.update import Update
from telegram_bot.messages.help import AUTH_HELP, UNAUTH_HELP
from telegram_bot.services.security import check_authentication


def help(update: Update, context: CallbackContext) -> None:
    '''Get Telegram Bot help message.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    if check_authentication(update.effective_chat):                             # Linked Telegram chat
        update.message.reply_text(AUTH_HELP, parse_mode=ParseMode.MARKDOWN_V2)
    else:                                                                       # Unlinked Telegram chat
        update.message.reply_text(UNAUTH_HELP, parse_mode=ParseMode.MARKDOWN_V2)
