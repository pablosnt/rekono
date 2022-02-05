from typing import List

from processes.models import Process
from projects.models import Project
from targets.models import Target, TargetPort
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.update import Update
from telegram_bot.messages.ask import (ASK_FOR_PROCESS, ASK_FOR_PROJECT,
                                       ASK_FOR_TARGET, ASK_FOR_TARGET_PORT,
                                       ASK_FOR_TOOL, NO_PROCESSES, NO_PROJECTS,
                                       NO_TARGET_PORTS, NO_TARGETS, NO_TOOLS)
from telegram_bot.models import TelegramChat
from tools.models import Tool


def send_message(update: Update, chat: TelegramChat, text: str) -> None:
    '''Send Telegram text message.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        text (str): Text message to send
    '''
    if hasattr(update, 'message') and getattr(update, 'message'):               # Standard update
        update.message.reply_text(text)
    else:                                                                       # Update from keyboard selection
        update.callback_query.bot.send_message(chat.chat_id, text=text)


def send_options(update: Update, chat: TelegramChat, text: str, keyboard: List[List[InlineKeyboardButton]]) -> None:
    '''Send Telegram options message.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        text (str): Text message to send
        keyboard (List[List[InlineKeyboardButton]]): Keyboard with the available options
    '''
    if hasattr(update, 'message') and getattr(update, 'message'):               # Standard update
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:                                                                       # Update from keyboard selection
        update.callback_query.bot.send_message(chat.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def ask_for_project(update: Update, chat: TelegramChat, next_state: int) -> int:
    '''Ask the user for choose one project.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        next_state (int): Next conversation state to call

    Returns:
        int: Next conversation state or end conversation
    '''
    projects = Project.objects.filter(members=chat.user).order_by('name').all()     # Get all user projects
    if not projects:                                                            # No projects found
        send_message(update, chat, NO_PROJECTS)
        return ConversationHandler.END                                          # End conversation
    else:
        # Build keyboard with the projects data
        keyboard = [[InlineKeyboardButton(p.name, callback_data=p.id) for p in projects]]
        send_options(update, chat, ASK_FOR_PROJECT, keyboard)
        return next_state                                                       # Go to next conversation state


def ask_for_target(update: Update, chat: TelegramChat, next_state: int) -> int:
    '''Ask the user for choose one target.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        next_state (int): Next conversation state to call

    Returns:
        int: Next conversation state or end conversation
    '''
    targets = Target.objects.filter(project=chat.project).order_by('target').all()  # Get all user targets
    if not targets:                                                             # No projects found
        send_message(update, chat, NO_TARGETS)
        return ConversationHandler.END                                          # End conversation
    else:
        # Build keyboard with the targets data
        keyboard = [[InlineKeyboardButton(t.target, callback_data=t.id) for t in targets]]
        send_options(update, chat, ASK_FOR_TARGET, keyboard)
        return next_state                                                       # Go to next conversation state


def ask_for_target_port(update: Update, chat: TelegramChat, next_state: int) -> int:
    '''Ask the user for choose one target port.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        next_state (int): Next conversation state to call

    Returns:
        int: Next conversation state or end conversation
    '''
    target_ports = TargetPort.objects.filter(target=chat.target).order_by('port').all()     # Get target ports
    if not target_ports:                                                        # No target ports found
        send_message(update, chat, NO_TARGET_PORTS)
        return ConversationHandler.END                                          # End conversation
    else:
        # Build keyboard with the target ports data
        keyboard = [[InlineKeyboardButton(tp.port, callback_data=tp.id) for tp in target_ports]]
        send_options(update, chat, ASK_FOR_TARGET_PORT, keyboard)
        return next_state                                                       # Go to next conversation state


def ask_for_process(update: Update, chat: TelegramChat, next_state: int) -> int:
    '''Ask the user for choose one process.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        next_state (int): Next conversation state to call

    Returns:
        int: Next conversation state or end conversation
    '''
    processes = Process.objects.order_by('name').all()
    if not processes:
        send_message(update, chat, NO_PROCESSES)
        return ConversationHandler.END                                          # End conversation
    else:
        # Build keyboard with the processes data
        keyboard = [[InlineKeyboardButton(p.name, callback_data=p.id) for p in processes]]
        send_options(update, chat, ASK_FOR_PROCESS, keyboard)
        return next_state                                                       # Go to next conversation state


def ask_for_tool(update: Update, chat: TelegramChat, next_state: int) -> int:
    '''Ask the user for choose one tool.

    Args:
        update (Update): Telegram Bot update
        chat (TelegramChat): Telegram chat entity
        next_state (int): Next conversation state to call

    Returns:
        int: Next conversation state or end conversation
    '''
    tools = Tool.objects.order_by('name').all()
    if not tools:
        send_message(update, chat, NO_TOOLS)
        return ConversationHandler.END                                          # End conversation
    else:
        # Build keyboard with the tools data
        keyboard = [[InlineKeyboardButton(t.name, callback_data=t.id) for t in tools]]
        send_options(update, chat, ASK_FOR_TOOL, keyboard)
        return next_state                                                       # Go to next conversation state
