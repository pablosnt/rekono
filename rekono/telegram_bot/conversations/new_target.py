from targets.serializers import TargetSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import PROJECT, STATES
from telegram_bot.conversations.ask import ask_for_project
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.selection import clear
from telegram_bot.conversations.states import CREATE
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.targets import ASK_FOR_NEW_TARGET, NEW_TARGET
from telegram_bot.security import get_chat


def new_target(update: Update, context: CallbackContext) -> int:
    '''Create new target via Telegram Bot.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if PROJECT in context.chat_data:                                        # Project already selected
            update.message.reply_text(ASK_FOR_NEW_TARGET)                       # Ask for the new target
            return CREATE                                                       # Go to target creation
        else:                                                                   # No selected project
            context.chat_data[STATES] = [(CREATE, ASK_FOR_NEW_TARGET)]
            return ask_for_project(update, context, chat)                       # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def create_target(update: Update, context: CallbackContext) -> int:
    '''Create new target.

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
        # Prepare target data
        serializer = TargetSerializer(data={'project': context.chat_data[PROJECT].id, 'target': update.message.text})
        if serializer.is_valid():                                               # Target is valid
            target = serializer.save()                                          # Create target
            update.message.reply_text(                                          # Confirm target creation
                NEW_TARGET.format(
                    target=escape_markdown(target.target, version=2),
                    target_type=escape_markdown(target.type, version=2),
                    project=escape_markdown(context.chat_data[PROJECT].name, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:                                                                   # Invalid target data
            # Send error details
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET)                       # Re-ask for the new target
            return CREATE                                                       # Repeat the current state
    return ConversationHandler.END                                              # End conversation
