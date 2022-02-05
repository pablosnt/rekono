from django.db.models import Q
from security.authorization.roles import Role
from telegram.update import Update
from telegram_bot.messages.security import AUTHN_ERROR, AUTHZ_ERROR
from telegram_bot.models import TelegramChat


def check_auditor(chat: TelegramChat) -> bool:
    if chat and chat.user:
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
