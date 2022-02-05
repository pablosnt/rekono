from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Operation has been cancelled')
    return ConversationHandler.END
