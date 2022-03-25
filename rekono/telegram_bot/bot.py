import logging

from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          Updater)
from telegram_bot.commands.basic import logout, start
from telegram_bot.commands.help import help
from telegram_bot.commands.selection import clear, show
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.execute import (execute, execute_process,
                                                execute_tool)
from telegram_bot.conversations.new_target import create_target, new_target
from telegram_bot.conversations.new_target_endpoint import (
    create_target_endpoint, new_target_endpoint)
from telegram_bot.conversations.new_target_port import (create_target_port,
                                                        new_target_port)
from telegram_bot.conversations.new_target_technology import (
    create_target_technology, new_target_technology)
from telegram_bot.conversations.new_target_vulnerability import (
    create_target_vulnerability, new_target_vulnerability)
from telegram_bot.conversations.select_project import project
from telegram_bot.conversations.selection import (select_configuration,
                                                  select_intensity,
                                                  select_process,
                                                  select_project,
                                                  select_target,
                                                  select_target_port,
                                                  select_tool, select_wordlist)
from telegram_bot.conversations.states import (CREATE, EXECUTE,
                                               SELECT_CONFIGURATION,
                                               SELECT_INTENSITY,
                                               SELECT_PROCESS, SELECT_PROJECT,
                                               SELECT_TARGET,
                                               SELECT_TARGET_PORT, SELECT_TOOL,
                                               SELECT_WORDLIST)
from telegram_bot.messages.help import get_my_commands

from rekono.settings import TELEGRAM_TOKEN

logger = logging.getLogger()                                                    # Rekono logger


def initialize() -> None:
    '''Initialize Telegram Bot.'''
    try:
        updater = Updater(token=TELEGRAM_TOKEN)                                 # Telegram client
        updater.bot.set_my_commands(get_my_commands())                          # Configure bot commands
    except Exception:
        logger.error('[Telegram Bot] Error during Telegram bot initialization')


def deploy() -> None:
    '''Start listenning for commands.'''
    try:
        updater = Updater(token=TELEGRAM_TOKEN)                                 # Telegram client
        updater.dispatcher.add_handler(CommandHandler('start', start))          # Start command
        updater.dispatcher.add_handler(CommandHandler('logout', logout))        # Logout command
        updater.dispatcher.add_handler(CommandHandler('help', help))            # Help command
        updater.dispatcher.add_handler(CommandHandler('showproject', show))     # Show selected project
        updater.dispatcher.add_handler(CommandHandler('clearproject', clear))   # Clear selected project
        updater.dispatcher.add_handler(ConversationHandler(                         # Select project
            entry_points=[CommandHandler('selectproject', project)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Create new target
            entry_points=[CommandHandler('newtarget', new_target)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                CREATE: [MessageHandler(Filters.text, create_target)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Create new target port
            entry_points=[CommandHandler('newport', new_target_port)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                CREATE: [MessageHandler(Filters.text, create_target_port)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Create new target endpoint
            entry_points=[CommandHandler('newendpoint', new_target_endpoint)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                SELECT_TARGET_PORT: [CallbackQueryHandler(select_target_port)],
                CREATE: [MessageHandler(Filters.text, create_target_endpoint)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Create new target technology
            entry_points=[CommandHandler('newtechnology', new_target_technology)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                SELECT_TARGET_PORT: [CallbackQueryHandler(select_target_port)],
                CREATE: [MessageHandler(Filters.text, create_target_technology)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Create new target vulnerability
            entry_points=[CommandHandler('newvulnerability', new_target_vulnerability)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                SELECT_TARGET_PORT: [CallbackQueryHandler(select_target_port)],
                CREATE: [MessageHandler(Filters.text, create_target_vulnerability)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Execute tool
            entry_points=[CommandHandler('tool', execute_tool)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                SELECT_TOOL: [CallbackQueryHandler(select_tool)],
                SELECT_WORDLIST: [CallbackQueryHandler(select_wordlist)],
                SELECT_CONFIGURATION: [CallbackQueryHandler(select_configuration)],
                SELECT_INTENSITY: [CallbackQueryHandler(select_intensity)],
                EXECUTE: [CallbackQueryHandler(execute)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Execute process
            entry_points=[CommandHandler('process', execute_process)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                SELECT_PROCESS: [CallbackQueryHandler(select_process)],
                SELECT_WORDLIST: [CallbackQueryHandler(select_wordlist)],
                SELECT_INTENSITY: [CallbackQueryHandler(select_intensity)],
                EXECUTE: [CallbackQueryHandler(execute)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.start_polling()                                                 # Start Telegram Bot
    except Exception:
        logger.error('[Telegram Bot] Error during Telegram bot deployment')
