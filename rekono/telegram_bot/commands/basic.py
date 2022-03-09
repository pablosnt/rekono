import logging

from security.otp import generate, get_expiration
from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.update import Update
from telegram_bot.messages.basic import LOGOUT, OTP, WELCOME
from telegram_bot.models import TelegramChat

logger = logging.getLogger()                                                    # Rekono logger


def start(update: Update, context: CallbackContext) -> None:
    '''Initialize Telegram Bot chat.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    if update.effective_chat and update.effective_message:
        chat, _ = TelegramChat.objects.update_or_create(                        # Create or update the Telegram chat
            defaults={'user': None, 'otp': generate(), 'otp_expiration': get_expiration()},
            chat_id=update.effective_chat.id
        )
        logger.info(f'[Security] New login request using the Telegram bot from the chat {chat.chat_id}')
        # Send welcome message including OTP to link Telegram Chat with an user account
        update.effective_message.reply_text(WELCOME, parse_mode=ParseMode.MARKDOWN_V2)
        update.effective_message.reply_text(OTP.format(otp=chat.otp), parse_mode=ParseMode.MARKDOWN_V2)


def logout(update: Update, context: CallbackContext) -> None:
    '''Unlink Telegram Bot chat for an user account.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    if update.effective_chat and update.effective_message:
        chat = TelegramChat.objects.filter(chat_id=update.effective_chat.id).first()    # Get Telegram chat by Id
        if chat:
            chat.delete()                                                       # Remove Telegram chat update
        if chat.user:
            logger.info(
                f'[Security] User {chat.user.id} has logged out from the Telegram bot',
                extra={'user': chat.user.id}
            )
        update.effective_message.reply_text(LOGOUT, parse_mode=ParseMode.MARKDOWN_V2)     # Send goodbye message
