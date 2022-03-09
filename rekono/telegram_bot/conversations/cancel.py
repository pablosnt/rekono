import logging

from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.context import (CONFIGURATION, INTENSITY, PROCESS, STATES,
                                  TARGET, TARGET_PORT, TOOL)
from telegram_bot.conversations.selection import clear
from telegram_bot.messages.conversations import CANCEL

logger = logging.getLogger()                                                    # Rekono logger


def cancel(update: Update, context: CallbackContext) -> int:
    '''Cancel current operation.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: End conversation
    '''
    clear(context, [STATES, TARGET, TARGET_PORT, PROCESS, TOOL, CONFIGURATION, INTENSITY])      # Clear Telegram context
    if update.effective_message:
        update.effective_message.reply_text(CANCEL)                             # Confirm cancellation
    logger.info('[Telegram Bot] Current operation has been cancelled')
    return ConversationHandler.END
