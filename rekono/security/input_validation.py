import re

from django.forms import ValidationError

NAME_REGEX = r'[\w\s\.\-]*'                                                     # Regex for names validation
TEXT_REGEX = r'[\w\s\.:,+\-\'"?¿¡!#%$€]*'                                       # Regex for text validation
ENDPOINT_REGEX = r'[\w\./#?&%]*'                                                # Regex for endpoint validation


def validate_name(value: str) -> None:
    '''Validate if name is valid based on regex.

    Args:
        value (str): Name value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    if not bool(re.fullmatch(NAME_REGEX, value)):
        raise ValidationError('Value contains unallowed characters')


def validate_text(value: str) -> None:
    '''Validate if text is valid based on regex.

    Args:
        value (str): Text value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    if not bool(re.fullmatch(TEXT_REGEX, value)):
        raise ValidationError('Value contains unallowed characters')


def validate_number(value: int) -> None:
    '''Validate if number is valid based on min and max values.

    Args:
        value (int): Number value

    Raises:
        ValidationError: Raised if value is lower or greater than the expected range
    '''
    if value < 1 or value > 999999:
        raise ValidationError('Invalid number')


def validate_endpoint(value: str) -> None:
    '''Validate if endpoint is valid based on regex.

    Args:
        value (str): Endpoint value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    if not bool(re.fullmatch(ENDPOINT_REGEX, value)):
        raise ValidationError('Invalid endpoint value')


def validate_time_amount(value: int) -> None:
    '''Validate if specific amount of time is valid based on min and max values.

    Args:
        value (int): Amount of time

    Raises:
        ValidationError: Raised if value is lower or greater than the expected range
    '''
    if value < 1 or value > 1000:
        raise ValidationError('Invalid time value')
