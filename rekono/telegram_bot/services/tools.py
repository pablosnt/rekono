from telegram_bot.models import TelegramChat
from tools.models import Tool


def save_tool_by_id(chat: TelegramChat, tool_id: int) -> Tool:
    '''Save tool as selected for one Telegram chat.

    Args:
        chat (TelegramChat): Telegram chat entity
        tool_id (int): Tool Id to select

    Returns:
        Project: Selected project entity
    '''
    tool = Tool.objects.get(pk=tool_id)                                         # Get tool by Id
    chat.tool = tool                                                            # Select tool
    chat.save(update_fields=['tool'])
    return tool
