from targets.models import Target
from telegram_bot.models import TelegramChat


def save_target(chat: TelegramChat, target: Target) -> Target:
    chat.target = target
    chat.save(update_fields=['target'])
    return target


def save_target_by_id(chat: TelegramChat, target_id: int) -> Target:
    target = Target.objects.get(pk=target_id)
    return save_target(chat, target)
