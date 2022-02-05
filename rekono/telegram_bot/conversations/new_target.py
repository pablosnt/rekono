from targets.serializers import TargetSerializer
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.conversations.ask import ask_for_project
from telegram_bot.conversations.cancel import cancel
from telegram_bot.messages.errors import create_error_message
from telegram_bot.messages.selection import SELECTED_PROJECT
from telegram_bot.messages.targets import ASK_FOR_NEW_TARGET, NEW_TARGET
from telegram_bot.services.projects import save_project_by_id
from telegram_bot.services.security import get_chat
from telegram_bot.services.targets import save_target

NT_SELECT_PROJECT = 0                                                           # First state: select project
NT_CREATE_TARGET = 1                                                            # Second state: create target


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
        if chat.project:                                                        # Project already selected
            update.message.reply_text(ASK_FOR_NEW_TARGET)                       # Ask for the new target
            return NT_CREATE_TARGET                                             # Go to target creation
        else:                                                                   # No selected project
            return ask_for_project(update, chat, NT_SELECT_PROJECT)             # Ask for project selection
    return ConversationHandler.END                                              # Unauthorized: end conversation


def select_project_for_new_target(update: Update, context: CallbackContext) -> int:
    '''Select project before new target creation.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        project = save_project_by_id(chat, int(update.callback_query.data))     # Save selected project
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))     # Confirm selection
        update.callback_query.bot.send_message(chat.chat_id, text=ASK_FOR_NEW_TARGET)   # Ask for the new target
        return NT_CREATE_TARGET                                                 # Go to target creation
    update.callback_query.answer()                                              # Empty answer
    return ConversationHandler.END                                              # Unauthorized: end conversation


def create_target(update: Update, context: CallbackContext) -> int:
    '''Create new target.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat:
        if update.message.text == '/cancel':                                    # Check if cancellation is requested
            return cancel(update, context)                                      # Cancel operation
        # Prepare target data
        serializer = TargetSerializer(data={'project': chat.project.id, 'target': update.message.text})
        if serializer.is_valid():                                               # Target is valid
            target = serializer.save()                                          # Create target
            save_target(chat, target)                                           # Select target for future operations
            update.message.reply_text(                                          # Confirm target creation
                NEW_TARGET.format(
                    target=escape_markdown(target.target, version=2),
                    target_type=escape_markdown(target.type, version=2),
                    project=escape_markdown(chat.project.name, version=2)
                ), parse_mode=ParseMode.MARKDOWN_V2
            )
        else:                                                                   # Invalid target data
            # Send error details
            update.message.reply_text(create_error_message(serializer.errors), parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(ASK_FOR_NEW_TARGET)                       # Re-ask for the new target
            return NT_CREATE_TARGET                                             # Repeat the current state
    return ConversationHandler.END                                              # End conversation
