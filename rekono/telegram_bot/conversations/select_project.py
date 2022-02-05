from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.conversations.ask import ask_for_project
from telegram_bot.messages.selection import create_selection_message
from telegram_bot.services.projects import save_project_by_id
from telegram_bot.services.security import get_chat

SP_SELECT_PROJECT = 0


def project(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        return ask_for_project(update, chat, SP_SELECT_PROJECT)
    return ConversationHandler.END


def select_project(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        project = save_project_by_id(chat, int(update.callback_query.data))
        update.callback_query.answer(SP_SELECT_PROJECT.format(project=project.name))
        update.callback_query.bot.send_message(chat.chat_id, text=create_selection_message(chat), parse_mode=ParseMode.MARKDOWN_V2)
    update.callback_query.answer()
    return ConversationHandler.END
