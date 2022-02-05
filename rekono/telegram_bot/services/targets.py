from targets.models import Target, TargetPort
from telegram_bot.models import TelegramChat


def save_target(chat: TelegramChat, target: Target) -> Target:
    chat.target = target
    chat.save(update_fields=['target'])
    return target


def save_target_by_id(chat: TelegramChat, target_id: int) -> Target:
    target = Target.objects.get(pk=target_id)
    return save_target(chat, target)


def save_target_port_by_id(chat: TelegramChat, target_port_id: int) -> TargetPort:
    target_port = TargetPort.objects.get(pk=target_port_id)
    chat.target_port = target_port
    chat.save(update_fields=['target_port'])
    return target_port
