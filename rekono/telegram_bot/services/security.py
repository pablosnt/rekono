from django.db.models import Q
from security.authorization.roles import Role
from telegram import Chat
from telegram.update import Update
from telegram_bot.messages.security import AUTHN_ERROR, AUTHZ_ERROR
from telegram_bot.models import TelegramChat


def check_authentication(chat: Chat) -> bool:
    if chat:
        return TelegramChat.objects.filter(chat_id=chat.id).exists()
    return False


def check_auditor(chat: Chat) -> bool:
    if chat:
        return chat.user.groups.filter(Q(name=str(Role.AUDITOR)) | Q(name=str(Role.ADMIN))).exists()
    return False


def get_chat(update: Update, auditor: bool = True) -> TelegramChat:
    if update.effective_chat:
        chat = TelegramChat.objects.filter(chat_id=update.effective_chat.id).first()
        if not chat:
            update.message.reply_text(AUTHN_ERROR)
        elif auditor and not check_auditor(chat):
            update.message.reply_text(AUTHZ_ERROR)
        else:
            return chat
