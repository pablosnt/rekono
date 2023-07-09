from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.conversations.ask import ask_for_project
from telegram_bot.security import get_chat


def project(update: Update, context: CallbackContext) -> int:
    '''Select project to be used in next operations via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        return ask_for_project(update, context, chat)                           # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation
