from typing import List

from processes.models import Process
from projects.models import Project
from targets.models import Target, TargetPort
from telegram import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram.utils.helpers import escape_markdown
from telegram_bot.context import (CONFIGURATION, INTENSITY, PROCESS, PROJECT,
                                  STATES, TARGET, TARGET_PORT, TOOL)
from telegram_bot.messages.selection import (SELECTED_CONFIGURATION,
                                             SELECTED_INTENSITY,
                                             SELECTED_PROCESS,
                                             SELECTED_PROJECT, SELECTED_TARGET,
                                             SELECTED_TARGET_PORT,
                                             SELECTED_TOOL, SELECTION)
from telegram_bot.models import TelegramChat
from telegram_bot.security import get_chat
from tools.models import Configuration, Tool


def next_state(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Get next conversation state to go to.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state
    '''
    if context.chat_data and STATES in context.chat_data and context.chat_data[STATES]:     # Configured next states
        state, action = context.chat_data[STATES][0]                            # Get first one: state and action
        context.chat_data[STATES] = context.chat_data[STATES][1:]               # Remove first state from the context
        if action:                                                              # If requiired action
            if isinstance(action, str) and update.callback_query and update.callback_query.bot:
                # Action is a text message
                update.callback_query.bot.send_message(chat.chat_id, text=action)
            elif callable(action):                                              # Action is an "ask for" function
                return action(update, context, chat)
        return state                                                            # Return next state
    return ConversationHandler.END                                              # End conversation


def select_project(update: Update, context: CallbackContext) -> int:
    '''Manage selected project.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.callback_query and update.callback_query.data:
        project = Project.objects.get(pk=int(update.callback_query.data))       # Get project by Id
        context.chat_data[PROJECT] = project                                    # Save selected project
        update.callback_query.answer(SELECTED_PROJECT.format(project=project.name))     # Confirm selection
        state = next_state(update, context, chat)                               # Get next conversation state
        if state == ConversationHandler.END and update.callback_query.bot:      # This is the last state
            update.callback_query.bot.send_message(                             # Send confirmation message
                chat.chat_id,
                text=SELECTION.format(project=escape_markdown(context.chat_data[PROJECT].name, version=2)),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        return state                                                            # Go to next state
    elif update.callback_query:
        update.callback_query.answer()                                          # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_target(update: Update, context: CallbackContext) -> int:
    '''Manage selected target.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.callback_query and update.callback_query.data:
        target = Target.objects.get(pk=int(update.callback_query.data))         # Get target by Id
        context.chat_data[TARGET] = target                                      # Save selected target
        update.callback_query.answer(SELECTED_TARGET.format(target=target.target))     # Confirm selection
        return next_state(update, context, chat)                                # Go to next state
    if update.callback_query:
        update.callback_query.answer()                                          # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_target_port(update: Update, context: CallbackContext) -> int:
    '''Manage selected target port.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.callback_query and update.callback_query.data:
        target_port = TargetPort.objects.get(pk=int(update.callback_query.data))    # Get target port by Id
        context.chat_data[TARGET_PORT] = target_port                            # Save selected target port
        update.callback_query.answer(SELECTED_TARGET_PORT.format(port=target_port.port))     # Confirm selection
        return next_state(update, context, chat)                                # Go to next state
    if update.callback_query:
        update.callback_query.answer()                                          # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_tool(update: Update, context: CallbackContext) -> int:
    '''Manage selected tool.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.callback_query and update.callback_query.data:
        tool = Tool.objects.get(pk=int(update.callback_query.data))             # Get tool by Id
        context.chat_data[TOOL] = tool                                          # Save selected tool
        update.callback_query.answer(SELECTED_TOOL.format(tool=tool.name))      # Confirm selection
        return next_state(update, context, chat)                                # Go to next state
    if update.callback_query:
        update.callback_query.answer()                                          # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_process(update: Update, context: CallbackContext) -> int:
    '''Manage selected process.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.callback_query and update.callback_query.data:
        process = Process.objects.get(pk=int(update.callback_query.data))       # Get process by Id
        context.chat_data[PROCESS] = process                                    # Save selected process
        update.callback_query.answer(SELECTED_PROCESS.format(process=process.name))     # Confirm selection
        return next_state(update, context, chat)                                # go to next state
    if update.callback_query:
        update.callback_query.answer()                                          # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_configuration(update: Update, context: CallbackContext) -> int:
    '''Manage selected configuration.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.callback_query and update.callback_query.data:
        configuration = Configuration.objects.get(pk=int(update.callback_query.data))   # Get configuration by Id
        context.chat_data[CONFIGURATION] = configuration                        # Save selected configuration
        # Confirm selection
        update.callback_query.answer(SELECTED_CONFIGURATION.format(configuration=configuration.name))
        return next_state(update, context, chat)                                # Go to next state
    if update.callback_query:
        update.callback_query.answer()                                          # Empty answer
    return ConversationHandler.END                                              # End conversation


def select_intensity(update: Update, context: CallbackContext) -> int:
    '''Manage selected intensity rank.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context

    Returns:
        int: Conversation state
    '''
    chat = get_chat(update)                                                     # Get Telegram chat
    if chat and context.chat_data is not None and update.callback_query and update.callback_query.data:
        context.chat_data[INTENSITY] = update.callback_query.data.upper()       # Save selected intensity
        # Confirm selection
        update.callback_query.answer(SELECTED_INTENSITY.format(intensity=update.callback_query.data.capitalize()))
        return next_state(update, context, chat)                                # Go to next state
    if update.callback_query:
        update.callback_query.answer()                                          # Empty answer
    return ConversationHandler.END                                              # End conversation


def clear(context: CallbackContext, keys: List[str]) -> None:
    '''Clear Telegram context.

    Args:
        context (CallbackContext): Telegram Bot context
        keys (List[str]): Field keys to clear
    '''
    if not context.chat_data:
        return
    for key in keys:                                                            # For each key
        if key in context.chat_data:                                            # Key found in context
            context.chat_data.pop(key)                                          # Remove field from Telegram context
