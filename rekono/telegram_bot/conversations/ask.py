from typing import List

from authentications.enums import AuthenticationType
from input_types.enums import InputTypeNames
from processes.models import Process
from projects.models import Project
from resources.models import Wordlist
from targets.models import Target, TargetPort
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.update import Update
from telegram_bot.context import COMMAND, PROCESS, PROJECT, TARGET, TOOL
from telegram_bot.conversations.states import (EXECUTE,
                                               SELECT_AUTHENTICATION_TYPE,
                                               SELECT_CONFIGURATION,
                                               SELECT_INTENSITY,
                                               SELECT_PROCESS, SELECT_PROJECT,
                                               SELECT_TARGET,
                                               SELECT_TARGET_PORT, SELECT_TOOL,
                                               SELECT_WORDLIST)
from telegram_bot.messages.ask import (ASK_FOR_AUTHENTICATION_TYPE,
                                       ASK_FOR_CONFIGURATION,
                                       ASK_FOR_INTENSITY, ASK_FOR_PROCESS,
                                       ASK_FOR_PROJECT, ASK_FOR_TARGET,
                                       ASK_FOR_TARGET_PORT, ASK_FOR_TOOL,
                                       ASK_FOR_WORDLIST, NO_PROCESSES,
                                       NO_PROJECTS, NO_TARGET_PORTS,
                                       NO_TARGETS)
from telegram_bot.messages.execution import confirmation_message
from telegram_bot.models import TelegramChat
from tools.enums import IntensityRank
from tools.models import Configuration, Input, Tool


def send_message(update: Update, chat: TelegramChat, text: str) -> None:
    '''Send Telegram text message.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        text (str): Text message to send
    '''
    if update.effective_message:                                                # Standard update
        update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)
    elif update.callback_query and update.callback_query.bot:
        # Update from keyboard selection
        update.callback_query.bot.send_message(chat.chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)


def send_options(
    update: Update,
    chat: TelegramChat,
    text: str,
    keyboard: List[InlineKeyboardButton],
    per_row: int
) -> None:
    '''Send Telegram options message.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        text (str): Text message to send
        keyboard (List[InlineKeyboardButton]): Keyboard buttons for each available option
        per_row (int): Number of keyboard buttons to include by row
    '''
    keyboard_by_row = []
    for i in range(0, len(keyboard), per_row):                                  # For each row
        keyboard_by_row.append(keyboard[i:i + per_row])                         # Get keyboard buttons for this row
    if update.effective_message:                                                # Standard update
        update.effective_message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard_by_row),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    elif update.callback_query and update.callback_query.bot:
        # Update from keyboard selection
        update.callback_query.bot.send_message(
            chat.chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard_by_row),
            parse_mode=ParseMode.MARKDOWN_V2
        )


def ask_for_project(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one project.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    projects = Project.objects.filter(members=chat.user).order_by('name').all()     # Get all user projects
    if not projects:                                                            # No projects found
        send_message(update, chat, NO_PROJECTS)
        return ConversationHandler.END                                          # End conversation
    else:
        # Create keyboard buttons with the projects data
        keyboard = [InlineKeyboardButton(p.name, callback_data=p.id) for p in projects]
        send_options(update, chat, ASK_FOR_PROJECT, keyboard, 3)
        return SELECT_PROJECT                                                   # Go to selected project management


def ask_for_target(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one target.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    targets = []
    if context.chat_data:
        # Get all user targets
        targets = Target.objects.filter(project=context.chat_data[PROJECT]).order_by('target').all()
    if not targets:                                                             # No targets found
        send_message(update, chat, NO_TARGETS)
        return ConversationHandler.END                                          # End conversation
    else:
        # Create keyboard buttons with the targets data
        keyboard = [InlineKeyboardButton(t.target, callback_data=t.id) for t in targets]
        send_options(update, chat, ASK_FOR_TARGET, keyboard, 3)
        return SELECT_TARGET                                                    # Go to selected target management


def ask_for_target_port(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one target port.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    target_ports = []
    if context.chat_data:
        if context.chat_data[COMMAND] == 'newauth':
            # Get target ports without authentication by selected target
            target_ports = TargetPort.objects.filter(
                target=context.chat_data[TARGET],
                authentication=None
            ).order_by('port').all()
        else:
            # Get target ports by selected target
            target_ports = TargetPort.objects.filter(target=context.chat_data[TARGET]).order_by('port').all()
    if not target_ports:                                                        # No target ports found
        send_message(update, chat, NO_TARGET_PORTS)
        return ConversationHandler.END                                          # End conversation
    else:
        # Create keyboard buttons with the target ports data
        keyboard = [InlineKeyboardButton(tp.port, callback_data=tp.id) for tp in target_ports]
        send_options(update, chat, ASK_FOR_TARGET_PORT, keyboard, 5)
        return SELECT_TARGET_PORT                                               # Go to selected target port management


def ask_for_authentication_type(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one authentication type.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    authentication_types = AuthenticationType.values                            # Get authentication types
    if context.chat_data and context.chat_data[COMMAND] == 'newport':
        authentication_types.append('None')                                     # New ports could haven't authentication
    # Create keyboard buttons with the authentication types
    keyboard = [InlineKeyboardButton(t, callback_data=t) for t in authentication_types]
    send_options(update, chat, ASK_FOR_AUTHENTICATION_TYPE, keyboard, 3)
    return SELECT_AUTHENTICATION_TYPE                                           # Go to selected auth type management


def ask_for_process(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one process.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    processes = Process.objects.order_by('name').all()                          # Get all processes
    if not processes:
        send_message(update, chat, NO_PROCESSES)
        return ConversationHandler.END                                          # End conversation
    else:
        # Create keyboard buttons with the processes data
        keyboard = [InlineKeyboardButton(p.name, callback_data=p.id) for p in processes]
        send_options(update, chat, ASK_FOR_PROCESS, keyboard, 3)
        return SELECT_PROCESS                                                   # Go to selected process management


def ask_for_tool(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one tool.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    tools = Tool.objects.order_by('name').all()                                 # Get all tools
    # Create keyboard buttons with the tools data
    keyboard = [InlineKeyboardButton(t.name, callback_data=t.id) for t in tools]
    send_options(update, chat, ASK_FOR_TOOL, keyboard, 2)
    return SELECT_TOOL                                                          # Go to selected tool management


def ask_for_configuration(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one configuration.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    configurations = []
    if context.chat_data:
        # Get configurations by selected tool
        configurations = Configuration.objects.filter(tool=context.chat_data[TOOL]).order_by('name').all()
    # Create keyboard buttons with the configurations data
    keyboard = [InlineKeyboardButton(c.name, callback_data=c.id) for c in configurations]
    send_options(update, chat, ASK_FOR_CONFIGURATION, keyboard, 2)
    return SELECT_CONFIGURATION                                                 # Go to selected config management


def ask_for_wordlist(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one wordlist.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    wordlists = Wordlist.objects.all()                                          # Get all wordlists
    # Create keyboard buttons with the wordlists data
    keyboard = [InlineKeyboardButton(f'{w.name} - {w.type}', callback_data=w.id) for w in wordlists]
    tools_with_required_wordlists = ['Gobuster']                                # Tools with required wordlists
    check_if_wordlist_is_required = None
    if (                                                                        # Filter inputs by tool
        context.chat_data is not None and
        context.chat_data.get(TOOL) and
        context.chat_data.get(TOOL).name not in tools_with_required_wordlists
    ):
        check_if_wordlist_is_required = {'argument__tool': context.chat_data[TOOL]}
    elif (                                                                      # Filter inputs by process
        context.chat_data is not None and
        context.chat_data.get(PROCESS) and
        not context.chat_data[PROCESS].steps.filter(tool__name__in=tools_with_required_wordlists).exists()
    ):
        check_if_wordlist_is_required = {'argument__tool__in': context.chat_data[PROCESS].steps.all().values('tool')}
    if check_if_wordlist_is_required:
        check_if_wordlist_is_required.update({                                  # Base arguments to check if required
            'argument__required': True,
            'type__name': InputTypeNames.WORDLIST
        })
        if not Input.objects.filter(**check_if_wordlist_is_required).exists():  # Check if wordlist is required
            keyboard.append(InlineKeyboardButton('Default tools wordlists', callback_data='Default tools wordlists'))
    send_options(update, chat, ASK_FOR_WORDLIST, keyboard, 1)
    return SELECT_WORDLIST                                                      # Go to selected wordlist management


def ask_for_intensity(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user to choose one intensity rank.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    intensities = IntensityRank.names                                           # Get all intensities
    if context.chat_data and TOOL in context.chat_data:                         # Tool is selected
        # Get available intensities for selected tool
        intensities = [IntensityRank(i.value).name for i in context.chat_data[TOOL].intensities.order_by('value').all()]
    intensities.reverse()                                                       # Show harder intensities first
    # Create keyboard buttons with the intensities data
    keyboard = [InlineKeyboardButton(i.capitalize(), callback_data=i) for i in intensities]
    send_options(update, chat, ASK_FOR_INTENSITY, keyboard, 5)
    return SELECT_INTENSITY                                                     # Go to selected intensity management


def ask_for_execution_confirmation(update: Update, context: CallbackContext, chat: TelegramChat) -> int:
    '''Ask the user for confirmation before start execution.

    Args:
        update (Update): Telegram Bot update
        context (CallbackContext): Telegram Bot context
        chat (TelegramChat): Telegram chat entity

    Returns:
        int: Next conversation state or end conversation
    '''
    keyboard = [                                                                # Create keyboard buttons
        InlineKeyboardButton('Yes', callback_data='yes'),                       # Confirm execution
        InlineKeyboardButton('No', callback_data='no')                          # Cancel execution
    ]
    send_options(update, chat, confirmation_message(context), keyboard, 2)
    return EXECUTE                                                              # Go to execution management
