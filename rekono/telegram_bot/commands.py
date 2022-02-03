from security.crypto import generate_otp
from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.update import Update
from telegram_bot.messages.basic import LOGOUT, WELCOME
from telegram_bot.messages.help import AUTH_HELP, UNAUTH_HELP
from telegram_bot.models import TelegramChat
from security.otp import get_expiration


def start(update: Update, context: CallbackContext) -> None:
    '''Initialize Telegram Bot chat.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    if update.effective_chat:
        chat, _ = TelegramChat.objects.update_or_create(                        # Create or update the Telegram chat
            defaults={'user': None, 'otp': generate_otp(), 'otp_expiration': get_expiration()},
            chat_id=update.effective_chat.id
        )
        # Send welcome message including OTP to link Telegram Chat with an user account
        context.bot.send_message(chat.chat_id, text=WELCOME.format(otp=chat.otp), parse_mode=ParseMode.MARKDOWN_V2)


def logout(update: Update, context: CallbackContext) -> None:
    '''Unlink Telegram Bot chat for an user account.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    if update.effective_chat:
        chat = TelegramChat.objects.filter(chat_id=update.effective_chat.id).first()    # Get Telegram chat by Id
        if chat:
            chat.delete()
        # Send goodbye message
        context.bot.send_message(update.effective_chat.id, text=LOGOUT, parse_mode=ParseMode.MARKDOWN_V2)


def help(update: Update, context: CallbackContext) -> None:
    '''Get Telegram Bot help message.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
    '''
    if update.effective_chat:
        if TelegramChat.objects.filter(chat_id=update.effective_chat.id).exists():  # Linked Telegram chat
            context.bot.send_message(update.effective_chat.id, text=AUTH_HELP, parse_mode=ParseMode.MARKDOWN_V2)
        else:                                                                   # Unlinked Telegram chat
            context.bot.send_message(update.effective_chat.id, text=UNAUTH_HELP, parse_mode=ParseMode.MARKDOWN_V2)
