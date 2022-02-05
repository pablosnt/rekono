from telegram import ParseMode
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          Updater)
from telegram_bot.commands.basic import logout, start
from telegram_bot.commands.help import help
from telegram_bot.commands.selection import clear, clear_target, show
from telegram_bot.conversations.cancel import cancel
from telegram_bot.conversations.new_target import (
    NT_CREATE_TARGET, NT_SELECT_PROJECT, create_target, new_target,
    select_project_for_new_target)
from telegram_bot.conversations.new_target_port import (
    NTP_CREATE_TARGET_PORT, NTP_SELECT_PROJECT, NTP_SELECT_TARGET,
    create_target_port, new_target_port, select_project_for_new_target_port,
    select_target_for_new_target_port)
from telegram_bot.conversations.select_project import (SP_SELECT_PROJECT,
                                                       project, select_project)

from rekono.settings import TELEGRAM_TOKEN


def send_message(chat_id: int, text: str) -> None:
    '''Send Telegram message.

    Args:
        chat_id (int): Destinatary Telegram chat Id
        text (str): Text message with Markdown style
    '''
    updater = Updater(token=TELEGRAM_TOKEN)                                     # Telegram client
    updater.bot.send_message(chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)  # Send Telegram text message


def deploy() -> None:
    '''Start listenning for commands.'''
    updater = Updater(token=TELEGRAM_TOKEN)                                     # Telegram client
    updater.dispatcher.add_handler(CommandHandler('start', start))              # Start command
    updater.dispatcher.add_handler(CommandHandler('logout', logout))            # Logout command
    updater.dispatcher.add_handler(CommandHandler('help', help))                # Help command
    updater.dispatcher.add_handler(CommandHandler('showselection', show))
    updater.dispatcher.add_handler(CommandHandler('clearselection', clear))
    updater.dispatcher.add_handler(CommandHandler('clearproject', clear))
    updater.dispatcher.add_handler(CommandHandler('cleartarget', clear_target))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('selectproject', project)],
        states={
            SP_SELECT_PROJECT: [CallbackQueryHandler(select_project)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_chat=True
    ))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('newtarget', new_target)],
        states={
            NT_SELECT_PROJECT: [CallbackQueryHandler(select_project_for_new_target)],
            NT_CREATE_TARGET: [MessageHandler(Filters.text, create_target)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_chat=True
    ))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('newtargetport', new_target_port)],
        states={
            NTP_SELECT_PROJECT: [CallbackQueryHandler(select_project_for_new_target_port)],
            NTP_SELECT_TARGET: [CallbackQueryHandler(select_target_for_new_target_port)],
            NTP_CREATE_TARGET_PORT: [MessageHandler(Filters.text, create_target_port)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_chat=True
    ))
    updater.start_polling()                                                     # Start Telegram Bot
