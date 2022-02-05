from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.conversations.ask import ask_for_tool
from telegram_bot.messages.selection import (SELECTED_TOOL,
                                             create_selection_message)
from telegram_bot.services.security import get_chat
from telegram_bot.services.tools import save_tool_by_id

ST_SELECT_TOOL = 0                                                              # First state: select tool


def tool(update: Update, context: CallbackContext) -> int:
    '''Select tool to be used via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        return ask_for_tool(update, chat, ST_SELECT_TOOL)                       # Ask for tool selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_tool(update: Update, context: CallbackContext) -> int:
    '''Select tool.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    update.callback_query.answer()                                              # Empty answer
    if chat:
        tool = save_tool_by_id(chat, int(update.callback_query.data))           # Save selected tool
        update.callback_query.answer(SELECTED_TOOL.format(tool=tool.name))      # Confirm selection
        update.callback_query.bot.send_message(                                 # Show selection status
            chat.chat_id,
            text=create_selection_message(chat),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    return ConversationHandler.END                                              # End conversation
