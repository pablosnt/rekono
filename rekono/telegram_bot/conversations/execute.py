from tasks.serializers import TaskSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.context import (CONFIGURATION, INTENSITY, PROCESS, PROJECT,
                                  STATES, TARGET, TOOL)
from telegram_bot.conversations.ask import (ask_for_configuration,
                                            ask_for_execution_confirmation,
                                            ask_for_intensity, ask_for_process,
                                            ask_for_project, ask_for_target,
                                            ask_for_tool)
from telegram_bot.conversations.selection import clear
from telegram_bot.messages.conversations import CANCEL
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.execution import EXECUTION_LAUNCHED
from telegram_bot.security import get_chat


def execute_tool(update: Update, context: CallbackContext) -> int:
    '''Execute tool via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if PROJECT in context.chat_data:
            context.chat_data[STATES] = [
                (None, ask_for_tool),
                (None, ask_for_configuration),
                (None, ask_for_intensity),
                (None, ask_for_execution_confirmation)
            ]
            return ask_for_target(update, context, chat)
        else:
            context.chat_data[STATES] = [
                (None, ask_for_target),
                (None, ask_for_tool),
                (None, ask_for_configuration),
                (None, ask_for_intensity),
                (None, ask_for_execution_confirmation)
            ]
            return ask_for_project(update, context, chat)
    return ConversationHandler.END                                              # Unauthorized: end conversation


def execute_process(update: Update, context: CallbackContext) -> int:
    '''Execute process via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if PROJECT in context.chat_data:
            context.chat_data[STATES] = [
                (None, ask_for_process),
                (None, ask_for_intensity),
                (None, ask_for_execution_confirmation)
            ]
            return ask_for_target(update, context, chat)
        else:
            context.chat_data[STATES] = [
                (None, ask_for_target),
                (None, ask_for_process),
                (None, ask_for_intensity),
                (None, ask_for_execution_confirmation)
            ]
            return ask_for_project(update, context, chat)
    return ConversationHandler.END                                              # Unauthorized: end conversation


def execute(update: Update, context: CallbackContext) -> int:
    '''Execute tool.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    clear(context, [STATES])
    chat = get_chat(update)                                                     # Get Telegram chat
    update.callback_query.answer()                                              # Empty answer
    if chat:
        if update.callback_query.data.lower() == 'yes':
            task_data = {
                'target_id': context.chat_data[TARGET].id,
                'intensity_rank': context.chat_data[INTENSITY],
                'executor': chat.user
            }
            if TOOL in context.chat_data:
                task_data.update({
                    'tool_id': context.chat_data[TOOL].id,
                    'configuration_id': context.chat_data[CONFIGURATION].id
                })
            elif PROCESS in context.chat_data:
                task_data['process_id'] = context.chat_data[PROCESS].id
            serializer = TaskSerializer(data=task_data)
            if serializer.is_valid():
                task = serializer.create(serializer.validated_data)
                update.callback_query.bot.send_message(chat.chat_id, text=EXECUTION_LAUNCHED.format(id=task.id))
            else:
                update.callback_query.bot.send_message(
                    chat.chat_id,
                    text=create_error_message(serializer.errors),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
        else:
            update.callback_query.bot.send_message(chat.chat_id, text=CANCEL)
    clear(context, [TARGET, INTENSITY, TOOL, CONFIGURATION, PROCESS])
    return ConversationHandler.END                                              # End conversation
