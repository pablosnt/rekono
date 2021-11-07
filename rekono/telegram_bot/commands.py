from security.crypto import generate_otp
from telegram_bot.messages import HELP, HELP_START, LOGOUT, WELCOME
from telegram_bot.models import TelegramChat
from users.models import User


def start(update, context):
    users = User.objects.filter(telegram_id=update.effective_chat.id).all()
    for user in users:
        user.telegram_id = None
        user.save()
    previous_chat = TelegramChat.objects.get(chat_id=update.effective_chat.id)
    if previous_chat:
        previous_chat.delete()
    chat = TelegramChat.objects.create(chat_id=update.effective_chat.id, start_token=generate_otp())
    context.bot.send_message(
        update.effective_chat.id,
        text=WELCOME.format(start_token=chat.start_token)
    )


def logout(update, context):
    user = User.objects.filter(telegram_id=update.effective_chat.id).first()
    if user:
        user.telegram_id = None
        user.save()
    context.bot.send_message(update.effective_chat.id, text=LOGOUT)


def help(update, context):
    if User.objects.filter(telegram_id=update.effective_chat.id).exists():
        context.bot.send_message(update.effective_chat.id, text=HELP)
    else:
        context.bot.send_message(update.effective_chat.id, text=HELP_START)
