import logging

from authentications.serializers import AuthenticationSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import (AUTH_TYPE, COMMAND, PROJECT, STATES, TARGET,
                                  TARGET_PORT)
from telegram_bot.conversations.ask import (ask_for_authentication_type,
                                            ask_for_project, ask_for_target,
                                            ask_for_target_port)
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.selection import clear
from telegram_bot.conversations.states import CREATE_RELATED
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.parameters import (ASK_FOR_NEW_AUTHENTICATION,
                                              NEW_AUTHENTICATION)
from telegram_bot.security import get_chat

logger = logging.getLogger()                                                    # Rekono logger


def new_authentication(update: Update, context: CallbackContext) -> int:
    '''Request new authentication creation via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None:
        context.chat_data[COMMAND] = 'newauth'                                  # Save command in the context
        if PROJECT in context.chat_data:                                        # Project already selected
            context.chat_data[STATES] = [                                       # Configure next steps
                (None, ask_for_target_port),
                (None, ask_for_authentication_type),
                (CREATE_RELATED, ASK_FOR_NEW_AUTHENTICATION)
            ]
            return ask_for_target(update, context, chat)                        # Ask for target selection
        else:                                                                   # No selected project
            context.chat_data[STATES] = [                                       # Configure next steps
                (None, ask_for_target),
                (None, ask_for_target_port),
                (None, ask_for_authentication_type),
                (CREATE_RELATED, ASK_FOR_NEW_AUTHENTICATION)
            ]
            return ask_for_project(update, context, chat)                       # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def create_authentication(update: Update, context: CallbackContext) -> int:
    '''Create new authentication via Telegram Bot.

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
        credential = None
        if name and ':' in name:
            name, credential = name.split(':', 1)
        serializer = AuthenticationSerializer(                                  # Prepare authentication data
            data={
                'target_port': context.chat_data[TARGET_PORT].id,
                'name': name,
                'credential': credential,
                'type': context.chat_data[AUTH_TYPE]
            }
        )
        if serializer.is_valid():                                               # Authentication is valid
            authentication = serializer.save()                                  # Create authentication
            logger.info(
                f'[Telegram Bot] New authentication {authentication.id} has been created',
                extra={'user': chat.user.id}
            )
            update.effective_message.reply_text(                                # Confirm authentication creation
                NEW_AUTHENTICATION.format(
                    name=escape_markdown(authentication.name, version=2),
                    target=escape_markdown(authentication.target_port.target.target, version=2),
                    port=escape_markdown(str(authentication.target_port.port), version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            logger.info(
                '[Telegram Bot] Attempt of input technology creation with invalid data',
                extra={'user': chat.user.id}
            )
            update.effective_message.reply_text(                                # Send error details
                create_error_message(serializer.errors),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            update.effective_message.reply_text(ASK_FOR_NEW_AUTHENTICATION)     # Re-ask for the new authentication
            return CREATE_RELATED                                               # Repeat the current state
    clear(context, [TARGET_PORT, AUTH_TYPE])                                    # Clear Telegram context
    return ConversationHandler.END                                              # End conversation
