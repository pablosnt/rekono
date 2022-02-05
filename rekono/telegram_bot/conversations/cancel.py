from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.messages.conversations import CANCEL


def cancel(update: Update, context: CallbackContext) -> int:
    '''Cancel current operation.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: End conversation
    '''
    update.message.reply_text(CANCEL)
    return ConversationHandler.END
