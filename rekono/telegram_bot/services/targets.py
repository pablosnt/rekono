from targets.models import Target, TargetPort
from telegram_bot.models import TelegramChat


def save_target(chat: TelegramChat, target: Target) -> Target:
    '''Save target as selected for one Telegram chat.

    Args:
        chat (TelegramChat): Telegram chat entity
        target (Target): Target entity to select

    Returns:
        Target: Selected target entity
    '''
    chat.target = target
    chat.save(update_fields=['target'])                                         # Select target
    return target


def save_target_by_id(chat: TelegramChat, target_id: int) -> Target:
    '''Save target as selected for one Telegram chat.

    Args:
        chat (TelegramChat): Telegram chat entity
        target_id (int): Target Id to select

    Returns:
        Target: Selected target entity
    '''
    target = Target.objects.get(pk=target_id)                                   # Get target by Id
    return save_target(chat, target)                                            # Save target as selected


def save_target_port_by_id(chat: TelegramChat, target_port_id: int) -> TargetPort:
    '''Save target port as selected for one Telegram chat.

    Args:
        chat (TelegramChat): Telegram chat entity
        target_port_id (int): Target port Id to select

    Returns:
        TargetPort: Selected target port entity
    '''
    target_port = TargetPort.objects.get(pk=target_port_id)                     # Get target port by Id
    chat.target_port = target_port                                              # Select target port
    chat.save(update_fields=['target_port'])
    return target_port
