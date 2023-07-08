import logging

from tasks.serializers import TaskSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.context import (CONFIGURATION, INTENSITY, PROCESS, PROJECT,
                                  STATES, TARGET, TOOL, WORDLIST)
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

logger = logging.getLogger()                                                    # Rekono logger


def execute_tool(update: Update, context: CallbackContext) -> int:
    '''Request tool execution via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None:
        if PROJECT in context.chat_data:                                        # Project already selected
            context.chat_data[STATES] = [                                       # Prepare next steps
                (None, ask_for_tool),
                (None, ask_for_configuration),
                (None, ask_for_intensity),
                (None, ask_for_execution_confirmation)
            ]
            return ask_for_target(update, context, chat)                        # Ask for target selection
        else:                                                                   # No selected project
            context.chat_data[STATES] = [                                       # Prepare next steps
                (None, ask_for_target),
                (None, ask_for_tool),
                (None, ask_for_configuration),
                (None, ask_for_intensity),
                (None, ask_for_execution_confirmation)
            ]
            return ask_for_project(update, context, chat)                       # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def execute_process(update: Update, context: CallbackContext) -> int:
    '''Request process execution via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None:
        if PROJECT in context.chat_data:                                        # Project already selected
            context.chat_data[STATES] = [                                       # Prepare next steps
                (None, ask_for_process),
                (None, ask_for_intensity),
                (None, ask_for_execution_confirmation)
            ]
            return ask_for_target(update, context, chat)                        # Ask for target selection
        else:                                                                   # No selected project
            context.chat_data[STATES] = [                                       # Prepare next steps
                (None, ask_for_target),
                (None, ask_for_process),
                (None, ask_for_intensity),
                (None, ask_for_execution_confirmation)
            ]
            return ask_for_project(update, context, chat)                       # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def execute(update: Update, context: CallbackContext) -> int:
    '''Launch execution.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    clear(context, [STATES])                                                    # Clear Telegram context
    chat = get_chat(update)                                                  # Get Telegram chat
    if (
        chat and
        context.chat_data and
        update.callback_query and
        update.callback_query.bot and
        update.callback_query.data
    ):
        update.callback_query.answer()                                          # Empty answer
        if update.callback_query.data.lower() == 'yes':                         # Check execution confirmation
            task_data = {                                                       # Prepare common execution data
                'target_id': context.chat_data[TARGET].id,
                'intensity_rank': context.chat_data[INTENSITY],
                'executor': chat.user
            }
            if TOOL in context.chat_data:                                       # Tool execution
                task_data.update({                                              # Add tool data
                    'tool_id': context.chat_data[TOOL].id,
                    'configuration_id': context.chat_data[CONFIGURATION].id
                })
            elif PROCESS in context.chat_data:                                  # Process execution
                task_data['process_id'] = context.chat_data[PROCESS].id         # Add process data
            if WORDLIST in context.chat_data:                                   # Wordlist selected
                task_data['wordlists'] = [context.chat_data[WORDLIST].id]       # Add wordlist data
            serializer = TaskSerializer(data=task_data)                         # Create Task serializer
            if serializer.is_valid():                                           # Task is valid
                task = serializer.save(executor=chat.user)                      # Create task
                logger.info(f'[Telegram Bot] New task {task.id} has been created', extra={'user': chat.user.id})
                # Confirm task creation
                update.callback_query.bot.send_message(chat.chat_id, text=EXECUTION_LAUNCHED.format(id=task.id))
            else:                                                               # Invalid task data
                logger.info('[Telegram Bot] Attempt of task creation with invalid data', extra={'user': chat.user.id})
                update.callback_query.bot.send_message(                         # Send error details
                    chat.chat_id,
                    text=create_error_message(serializer.errors),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
        else:
            update.callback_query.bot.send_message(chat.chat_id, text=CANCEL)   # User didn't confirm the execution
    clear(context, [TARGET, INTENSITY, TOOL, CONFIGURATION, PROCESS])           # Clear Telegram context
    return ConversationHandler.END                                              # End conversation
