import logging

from targets.serializers import TargetPortSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import COMMAND, PROJECT, STATES, TARGET, TARGET_PORT
from telegram_bot.conversations.ask import (ask_for_authentication_type,
                                            ask_for_project, ask_for_target)
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.selection import clear
from telegram_bot.conversations.states import CREATE, CREATE_RELATED
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.parameters import ASK_FOR_NEW_AUTHENTICATION
from telegram_bot.messages.targets import (ASK_FOR_NEW_TARGET_PORT,
                                           INVALID_TARGET_PORT,
                                           NEW_TARGET_PORT)
from telegram_bot.security import get_chat

logger = logging.getLogger()                                                    # Rekono logger


def new_target_port(update: Update, context: CallbackContext) -> int:
    '''Request new target port creation via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None:
        context.chat_data[COMMAND] = 'newport'                                  # Save command in the context
        if PROJECT in context.chat_data:                                        # Project already selected
            context.chat_data[STATES] = [                                       # Configure next steps
                (CREATE, ASK_FOR_NEW_TARGET_PORT),
                (CREATE_RELATED, ASK_FOR_NEW_AUTHENTICATION)
            ]
            return ask_for_target(update, context, chat)                        # Ask for target selection
        else:                                                                   # No selected project
            context.chat_data[STATES] = [                                       # Configure next steps
                (None, ask_for_target),
                (CREATE, ASK_FOR_NEW_TARGET_PORT),
                (CREATE_RELATED, ASK_FOR_NEW_AUTHENTICATION)
            ]
            return ask_for_project(update, context, chat)                       # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def create_target_port(update: Update, context: CallbackContext) -> int:
    '''Create new target port via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.effective_message and update.effective_message.text:
        if update.effective_message.text == '/cancel':                          # Check if cancellation is requested
            return cancel(update, context)                                      # Cancel operation
        try:
            port = int(update.effective_message.text)                           # Check if port is a valid number
        except ValueError:
            update.effective_message.reply_text(INVALID_TARGET_PORT)            # Invalid target port
            update.effective_message.reply_text(ASK_FOR_NEW_TARGET_PORT)        # Re-ask for the new target port
            return CREATE                                                       # Repeat the current state
        # Prepare target port data
        serializer = TargetPortSerializer(data={'target': context.chat_data[TARGET].id, 'port': port})
        if serializer.is_valid():                                               # Target port is valid
            target_port = serializer.save()                                     # Create target port
            logger.info(
                f'[Telegram Bot] New target port {target_port.id} has been created',
                extra={'user': chat.user.id}
            )
            update.effective_message.reply_text(                                # Confirm target port creation
                NEW_TARGET_PORT.format(
                    port=escape_markdown(str(target_port.port), version=2),
                    target=escape_markdown(target_port.target.target, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
            context.chat_data[TARGET_PORT] = target_port                        # Save new target port in the context
        else:                                                                   # Invalid target port data
            logger.info(
                '[Telegram Bot] Attempt of target port creation with invalid data',
                extra={'user': chat.user.id}
            )
            # Send error details
            update.effective_message.reply_text(
                create_error_message(serializer.errors),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            update.effective_message.reply_text(ASK_FOR_NEW_TARGET_PORT)        # Re-ask for the new target port
            return CREATE                                                       # Repeat the current state
        return ask_for_authentication_type(update, context, chat)               # Create authentication for this port
    clear(context, [TARGET])                                                    # Clear Telegram context
    return ConversationHandler.END                                              # End conversation
