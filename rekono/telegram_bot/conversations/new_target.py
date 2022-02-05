from targets.serializers import TargetSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.selection import ask_for_project
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.selection import SELECTED_PROJECT
from telegram_bot.messages.targets import ASK_FOR_NEW_TARGET, NEW_TARGET
from telegram_bot.services.projects import save_project_by_id
from telegram_bot.services.security import get_chat

NT_SELECT_PROJECT = 0
NT_CREATE_TARGET = 1


def new_target(update: Update, context: CallbackContext) -> int:
    '''Create new target via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation status
    '''
    chat = get_chat(update)
    if chat:
        if chat.project:
            update.message.reply_text(ASK_FOR_NEW_TARGET)
            return NT_CREATE_TARGET
        else:
            return ask_for_project(update, chat, NT_SELECT_PROJECT)
    return ConversationHandler.END


def select_project_for_new_target(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        project = save_project_by_id(chat, int(update.callback_query.data))
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))
        update.callback_query.bot.send_message(chat.chat_id, text=ASK_FOR_NEW_TARGET)
        return NT_CREATE_TARGET
    update.callback_query.answer()
    return ConversationHandler.END


def create_target(update: Update, context: CallbackContext) -> int:
    chat = get_chat(update)
    if chat:
        if update.message.text == '/cancel':
            return cancel(update, context)
        chat.target = None
        chat.save(update_fields=['target'])
        serializer = TargetSerializer(data={'project': chat.project.id, 'target': update.message.text})
        if serializer.is_valid():
            target = serializer.save()
            update.message.reply_text(
                NEW_TARGET.format(
                    target=escape_markdown(target.target, version=2),
                    target_type=escape_markdown(target.type, version=2),
                    project=escape_markdown(chat.project.name, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET)
            return NT_CREATE_TARGET
    return ConversationHandler.END
