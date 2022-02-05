'''Help messages.'''

from typing import List, Tuple

from telegram.utils.helpers import escape_markdown

from rekono.settings import DESCRIPTION

UNAUTH_HELP = 'To initialize Rekono Bot use the command /start'

HELP = [
    ('start', '', 'Initialize the Rekono bot'),
    ('logout', '', 'Unlink bot from your account'),
    ('help', '', 'Show this message'),
    ('selectproject', 'Selection', 'Select one project to use in next operations'),
    ('selecttarget', 'Selection', 'Select one target to use in next operations'),
    ('showselection', 'Selection', 'Show selected items'),
    ('clearselection', 'Selection', 'Unselect all selected items'),
    ('cleartarget', 'Selection', 'Unselect the selected target'),
    ('newtarget', 'Targets', 'Create new target'),
    ('newtargetport', 'Targets', 'Create new target port'),
    ('newtargetendpoint', 'Targets', 'Create new target endpoint')
]


def get_my_commands() -> List[Tuple[str, str]]:
    my_commands = []
    for commands, _, description in HELP:
        my_commands.append((commands[0], description))
    return my_commands


def get_help_message(commands: List[Tuple[str, str, str]] = HELP) -> str:
    message = f'{escape_markdown(DESCRIPTION, version=2)}\n\n'
    current_section = ''
    for command, section, description in commands:
        if section != current_section:
            message += f'\n*{section}*\n'
            current_section = section
        message += f'/{command} \- {escape_markdown(description, version=2)}\n'
    return message


def get_reader_help_message() -> str:
    return get_help_message([(c, d) for c, d, s in HELP if not s])
