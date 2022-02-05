from typing import Dict, List

from telegram.utils.helpers import escape_markdown

ERROR_MESSAGE = '''
*ERRORS*

'''


def create_error_message(errors: Dict[str, List[str]]) -> str:
    message = ERROR_MESSAGE
    for field, messages in errors.items():
        message += f'_{field}_    {escape_markdown(messages[0], version=2)}'
    return message
