import logging

from targets.serializers import TargetTechnologySerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import PROJECT, STATES, TARGET, TARGET_PORT
from telegram_bot.conversations.ask import (ask_for_project, ask_for_target,
                                            ask_for_target_port)
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.selection import clear
from telegram_bot.conversations.states import CREATE
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.targets import (ASK_FOR_NEW_TARGET_TECHNOLOGY,
                                           NEW_TARGET_TECHNOLOGY)
from telegram_bot.security import get_chat

logger = logging.getLogger()                                                    # Rekono logger


def new_target_technology(update: Update, context: CallbackContext) -> int:
    '''Request new target technology creation via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None:
        if PROJECT in context.chat_data:                                        # Project already selected
            # Configure next steps
            context.chat_data[STATES] = [(None, ask_for_target_port), (CREATE, ASK_FOR_NEW_TARGET_TECHNOLOGY)]
            return ask_for_target(update, context, chat)                        # Ask for target selection
        else:                                                                   # No selected project
            context.chat_data[STATES] = [                                       # Configure next steps
                (None, ask_for_target),
                (None, ask_for_target_port),
                (CREATE, ASK_FOR_NEW_TARGET_TECHNOLOGY)
            ]
            return ask_for_project(update, context, chat)                       # Ask for project creation
    return ConversationHandler.END                                              # Unauthorized: end conversation


def create_target_technology(update: Update, context: CallbackContext) -> int:
    '''Create new target technology via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    clear(context, [STATES, TARGET])                                            # Clear Telegram context
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.effective_message:
        if update.effective_message.text == '/cancel':                          # Check if cancellation is requested
            return cancel(update, context)                                      # Cancel operation
        name = update.effective_message.text
        version = None
        if name and ' - ' in name:
            aux = name.split(' - ')
            name = aux[0]
            version = aux[1]
        serializer = TargetTechnologySerializer(                                # Prepare target technology data
            data={'target_port': context.chat_data[TARGET_PORT].id, 'name': name, 'version': version}
        )
        if serializer.is_valid():                                               # Target technology is valid
            target_technology = serializer.save()                               # Create target technology
            logger.info(
                f'[Telegram Bot] New target technology {target_technology.id} has been created',
                extra={'user': chat.user.id}
            )
            update.effective_message.reply_text(                                # Confirm target technology creation
                NEW_TARGET_TECHNOLOGY.format(
                    name=escape_markdown(target_technology.name, version=2),
                    target=escape_markdown(target_technology.target_port.target.target, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:                                                                   # Invalid target technology data
            logger.info(
                '[Telegram Bot] Attempt of target technology creation with invalid data',
                extra={'user': chat.user.id}
            )
            # Send error details
            update.effective_message.reply_text(
                create_error_message(serializer.errors),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            # Re-ask for the new target technology
            update.effective_message.reply_text(ASK_FOR_NEW_TARGET_TECHNOLOGY)
            return CREATE                                                       # Repeat the current state
    clear(context, [TARGET_PORT])                                               # Clear Telegram context
    return ConversationHandler.END                                              # End conversation
