import logging
from typing import Optional

from system.models import System
from telegram.error import InvalidToken, Unauthorized
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          Updater)

from telegram_bot.commands.basic import logout, start
from telegram_bot.commands.help import help
from telegram_bot.commands.selection import clear, show
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.execute import (execute, execute_process,
                                                execute_tool)
from telegram_bot.conversations.new_authentication import (
    create_authentication, new_authentication)
from telegram_bot.conversations.new_input_technology import (
    create_input_technology, new_input_technology)
from telegram_bot.conversations.new_input_vulnerability import (
    create_input_vulnerability, new_input_vulnerability)
from telegram_bot.conversations.new_target import create_target, new_target
from telegram_bot.conversations.new_target_port import (create_target_port,
                                                        new_target_port)
from telegram_bot.conversations.select_project import project
from telegram_bot.conversations.selection import (select_authentication_type,
                                                  select_configuration,
                                                  select_intensity,
                                                  select_process,
                                                  select_project,
                                                  select_target,
                                                  select_target_port,
                                                  select_tool, select_wordlist)
from telegram_bot.conversations.states import (CREATE, CREATE_RELATED, EXECUTE,
                                               SELECT_AUTHENTICATION_TYPE,
                                               SELECT_CONFIGURATION,
                                               SELECT_INTENSITY,
                                               SELECT_PROCESS, SELECT_PROJECT,
                                               SELECT_TARGET,
                                               SELECT_TARGET_PORT, SELECT_TOOL,
                                               SELECT_WORDLIST)
from telegram_bot.messages.help import get_my_commands
from telegram_bot.token import handle_invalid_telegram_token

logger = logging.getLogger()                                                    # Rekono logger


def get_telegram_bot_name() -> Optional[str]:
    '''Get Telegram bot name using the Telegram token.

    Returns:
        Optional[str]: Telegram bot name
    '''
    try:
        updater = Updater(token=System.objects.first().telegram_bot_token)      # Telegram client
        return updater.bot.username
    except Exception:
        logger.error('[Telegram Bot] Error during Telegram bot name request')
        return None


def initialize() -> None:
    '''Initialize Telegram Bot.'''
    try:
        updater = Updater(token=System.objects.first().telegram_bot_token)      # Telegram client
        updater.bot.set_my_commands(get_my_commands())                          # Configure bot commands
    except (InvalidToken, Unauthorized):
        handle_invalid_telegram_token(initialize)
    except Exception:
        logger.error('[Telegram Bot] Error during Telegram bot initialization')


def deploy() -> None:
    '''Start listenning for commands.'''
    try:
        updater = Updater(token=System.objects.first().telegram_bot_token)      # Telegram client
        updater.dispatcher.add_handler(CommandHandler('start', start))          # Start command
        updater.dispatcher.add_handler(CommandHandler('logout', logout))        # Logout command
        updater.dispatcher.add_handler(CommandHandler('help', help))            # Help command
        updater.dispatcher.add_handler(CommandHandler('showproject', show))     # Show selected project
        updater.dispatcher.add_handler(CommandHandler('clearproject', clear))   # Clear selected project
        updater.dispatcher.add_handler(ConversationHandler(                     # Select project
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
                CREATE: [MessageHandler(Filters.text, create_target_port)],
                SELECT_AUTHENTICATION_TYPE: [CallbackQueryHandler(select_authentication_type)],
                CREATE_RELATED: [MessageHandler(Filters.text, create_authentication)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Create new authentication
            entry_points=[CommandHandler('newauth', new_authentication)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                SELECT_TARGET_PORT: [CallbackQueryHandler(select_target_port)],
                SELECT_AUTHENTICATION_TYPE: [CallbackQueryHandler(select_authentication_type)],
                CREATE_RELATED: [MessageHandler(Filters.text, create_authentication)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Create new input technology
            entry_points=[CommandHandler('newtechnology', new_input_technology)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                CREATE: [MessageHandler(Filters.text, create_input_technology)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.dispatcher.add_handler(ConversationHandler(                     # Create new input vulnerability
            entry_points=[CommandHandler('newvulnerability', new_input_vulnerability)],
            states={
                SELECT_PROJECT: [CallbackQueryHandler(select_project)],
                SELECT_TARGET: [CallbackQueryHandler(select_target)],
                CREATE: [MessageHandler(Filters.text, create_input_vulnerability)]
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
                SELECT_CONFIGURATION: [CallbackQueryHandler(select_configuration)],
                SELECT_INTENSITY: [CallbackQueryHandler(select_intensity)],
                SELECT_WORDLIST: [CallbackQueryHandler(select_wordlist)],
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
                SELECT_INTENSITY: [CallbackQueryHandler(select_intensity)],
                SELECT_WORDLIST: [CallbackQueryHandler(select_wordlist)],
                EXECUTE: [CallbackQueryHandler(execute)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True
        ))
        updater.start_polling()                                                 # Start Telegram Bot
    except (InvalidToken, Unauthorized):
        handle_invalid_telegram_token(deploy)
    except Exception:
        logger.error('[Telegram Bot] Error during Telegram bot deployment')
