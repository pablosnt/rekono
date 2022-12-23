from typing import List, Tuple

from rekono.settings import DESCRIPTION
from telegram.utils.helpers import escape_markdown

'''Help messages.'''


UNAUTH_HELP = 'To initialize Rekono Bot use the command /start'

HELP = [
    ('start', '', 'Initialize the Rekono bot'),
    ('logout', '', 'Unlink bot from your account'),
    ('help', '', 'Show this message'),
    ('selectproject', 'Selection', 'Select one project to be used in next operations'),
    ('showproject', 'Selection', 'Show selected project'),
    ('clearproject', 'Selection', 'Unselect the selected project'),
    ('newtarget', 'Targets', 'Create new target'),
    ('newport', 'Targets', 'Create new target port'),
    ('newauth', 'Targets', 'Create new authentication'),
    ('newtechnology', 'Parameters', 'Create new input technology'),
    ('newvulnerability', 'Parameters', 'Create new input vulnerability'),
    ('tool', 'Execution', 'Execute tool'),
    ('process', 'Execution', 'Execute process'),
    ('cancel', 'Common', 'Cancel current operation')
]


def get_my_commands() -> List[Tuple[str, str]]:
    '''Get Telegram commands from commands definition.

    Returns:
        List[Tuple[str, str]]: Telegram command list
    '''
    return [(c, d) for c, _, d, in HELP]


def get_help_message(commands: List[Tuple[str, str, str]] = HELP) -> str:
    '''Get help message from commands definition.

    Args:
        commands (List[Tuple[str, str, str]], optional): Command definition. If not set, default commands will be used

    Returns:
        str: Help message
    '''
    message = f'{escape_markdown(DESCRIPTION, version=2)}\n\n'                  # Add Rekono description
    current_section = ''
    for command, section, description in commands:                              # For each command
        if section != current_section:                                          # New section
            message += f'\n*{section}*\n'                                       # Add section title
            current_section = section
        message += f'/{command} \- {escape_markdown(description, version=2)}\n'     # Add command details
    return message


def get_reader_help_message() -> str:
    '''Get help message for reader user. Only basic commands will be included.

    Returns:
        str: Help message for reader user
    '''
    return get_help_message([(c, s, d) for c, s, d in HELP if not s])           # Get help message for basic commands
