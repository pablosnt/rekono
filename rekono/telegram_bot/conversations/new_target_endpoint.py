from targets.serializers import TargetEndpointSerializer
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
from telegram_bot.messages.targets import (ASK_FOR_NEW_TARGET_ENDPOINT,
                                           NEW_TARGET_ENDPOINT)
from telegram_bot.security import get_chat


def new_target_endpoint(update: Update, context: CallbackContext) -> int:
    '''Create new target endpoint via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if PROJECT in context.chat_data:
            context.chat_data[STATES] = [(None, ask_for_target_port), (CREATE, ASK_FOR_NEW_TARGET_ENDPOINT)]
            return ask_for_target(update, context, chat)                        # Ask for target selection
        else:
            context.chat_data[STATES] = [(None, ask_for_target), (None, ask_for_target_port), (CREATE, ASK_FOR_NEW_TARGET_ENDPOINT)]
            return ask_for_project(update, context, chat)
    return ConversationHandler.END                                              # Unauthorized: end conversation


def create_target_endpoint(update: Update, context: CallbackContext) -> int:
    '''Create new target endpoint.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    clear(context, [STATES, TARGET])
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if update.message.text == '/cancel':                                    # Check if cancellation is requested
            return cancel(update, context)                                      # Cancel operation
        serializer = TargetEndpointSerializer(                                  # Prepare target endpoint data
            data={'target_port': context.chat_data[TARGET_PORT].id, 'endpoint': update.message.text}
        )
        if serializer.is_valid():                                               # Target endpoint is valid
            target_endpoint = serializer.save()                                 # Create target endpoint
            update.message.reply_text(                                          # Confirm target endpoint creation
                NEW_TARGET_ENDPOINT.format(
                    endpoint=escape_markdown(target_endpoint.endpoint, version=2),
                    target=escape_markdown(target_endpoint.target_port.target.target, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:                                                                   # Invalid target endpoint data
            # Send error details
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET_ENDPOINT)              # Re-ask for the new target endpoint
            return CREATE                                                       # Repeat the current state
    clear(context, [TARGET_PORT])
    return ConversationHandler.END                                              # End conversation
