from processes.models import Process
from telegram_bot.models import TelegramChat


def save_process_by_id(chat: TelegramChat, process_id: int) -> Process:
    '''Save process as selected for one Telegram chat.

    Args:
        chat (TelegramChat): Telegram chat entity
        process_id (int): Process Id to select

    Returns:
        Project: Selected project entity
    '''
    process = Process.objects.get(pk=process_id)                                # Get process by Id
    chat.process = process                                                      # Select process
    chat.save(update_fields=['process'])
    return process
