from targets.serializers import TargetPortSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import PROJECT, STATES, TARGET
from telegram_bot.conversations.ask import ask_for_project, ask_for_target
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.selection import clear
from telegram_bot.conversations.states import CREATE
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.targets import (ASK_FOR_NEW_TARGET_PORT,
                                           INVALID_TARGET_PORT,
                                           NEW_TARGET_PORT)
from telegram_bot.security import get_chat


def new_target_port(update: Update, context: CallbackContext) -> int:
    '''Create new target port via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if PROJECT in context.chat_data:
            context.chat_data[STATES] = [(CREATE, ASK_FOR_NEW_TARGET_PORT)]
            return ask_for_target(update, context, chat)                        # Ask for target selection
        else:
            context.chat_data[STATES] = [(None, ask_for_target), (CREATE, ASK_FOR_NEW_TARGET_PORT)]
            return ask_for_project(update, context, chat)
    return ConversationHandler.END                                              # Unauthorized: end conversation


def create_target_port(update: Update, context: CallbackContext) -> int:
    '''Create new target port.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    clear(context, [STATES])
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if update.message.text == '/cancel':                                    # Check if cancellation is requested
            return cancel(update, context)                                      # Cancel operation
        try:
            port = int(update.message.text)                                     # Check if port is a valid number
        except ValueError:
            update.message.reply_text(INVALID_TARGET_PORT)                      # Invalid target port
            update.message.reply_text(ASK_FOR_NEW_TARGET_PORT)                  # Re-ask for the new target port
            return CREATE                                                       # Repeat the current state
        # Prepare target port data
        serializer = TargetPortSerializer(data={'target': context.chat_data[TARGET].id, 'port': port})
        if serializer.is_valid():                                               # Target port is valid
            target_port = serializer.save()                                     # Create target port
            update.message.reply_text(                                          # Confirm target port creation
                NEW_TARGET_PORT.format(
                    port=escape_markdown(str(target_port.port), version=2),
                    target=escape_markdown(target_port.target.target, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:                                                                   # Invalid target port data
            # Send error details
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET_PORT)                  # Re-ask for the new target port
            return CREATE                                                       # Repeat the current state
    clear(context, [TARGET])
    return ConversationHandler.END                                              # End conversation
