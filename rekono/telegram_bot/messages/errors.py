from typing import Dict, List

from telegram.utils.helpers import escape_markdown

'''Error messages.'''

AUTHN_ERROR = 'You have to link your Rekono account before using the Telegram Bot. Use the command /start'
AUTHZ_ERROR = 'You are not authorized to perform this operation'


def create_error_message(errors: Dict[str, List[str]]) -> str:
    '''Create error message from serializer errors.

    Args:
        errors (Dict[str, List[str]]): Serializer errors

    Returns:
        str: Text message with error details
    '''
    message = '*ERRORS*\n'
    for field, messages in errors.items():                                      # For each invalid field
        message += f'_{field}_    {escape_markdown(messages[0], version=2)}'    # Include first error message
    return message
