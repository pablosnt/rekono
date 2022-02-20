from typing import Union

from django.db.models import Q
from security.authorization.roles import Role
from telegram.update import Update
from telegram_bot.messages.errors import AUTHN_ERROR, AUTHZ_ERROR
from telegram_bot.models import TelegramChat


def check_auditor(chat: TelegramChat) -> bool:
    '''Check if a Telegram chat is used by an Auditor or an Admin.

    Args:
        chat (TelegramChat): Telegram chat to verify

    Returns:
        bool: Indicate if the chat is used by an Auditor or an Admin
    '''
    if chat and chat.user:
        # Check if user role is Auditor or Admin
        return chat.user.groups.filter(Q(name=str(Role.AUDITOR)) | Q(name=str(Role.ADMIN))).exists()
    return False                                                                # Chat not found or unlinked


def get_chat(update: Update, auditor: bool = True) -> Union[TelegramChat, None]:
    '''Get Telegram chat entity after checking linked account and user role.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        TelegramChat: Telegram chat entity if the user is authorized
    '''
    if update.effective_chat and update.message:                                # Chat Id from the update
        # Get chat entity
        chat = TelegramChat.objects.filter(chat_id=update.effective_chat.id, user__is_active=True).first()
        if not chat:                                                            # No chat found
            update.message.reply_text(AUTHN_ERROR)                              # Authentication error
        elif auditor and not check_auditor(chat):                               # User is not auditor
            update.message.reply_text(AUTHZ_ERROR)                              # Authorization error
        else:
            return chat                                                         # Chat is authorized
    return None                                                                 # Unauthorized chat
