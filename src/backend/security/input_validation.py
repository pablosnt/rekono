import logging
import re
from urllib.parse import urlparse

from django.forms import ValidationError

logger = logging.getLogger()                                                    # Rekono logger

IP_RANGE_REGEX = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}'                  # Regex for IP ranges like 10.10.10.1-20
NAME_REGEX = r'[\wÀ-ÿ\s\.\-\[\]()@]{0,120}'                                     # Regex for names validation
TEXT_REGEX = r'[\wÀ-ÿ\s\.:,+\-\'"?¿¡!#%$€\[\]()]{0,300}'                        # Regex for text validation
PATH_REGEX = r'[\w\./#?&%$\\]{0,500}'                                           # Regex for path validation
CVE_REGEX = r'CVE-\d{4}-\d{1,7}'                                                # Regex for CVE validation
DD_KEY_REGEX = r'[\da-z]{40}'                                                   # Regex for Defect-Dojo key validation
TELEGRAM_TOKEN_REGEX = r'\d{10}:[\w\-]{35}'                                     # Regex for Telegram token validation
CREDENTIAL_REGEX = r'[\w\./\-=\+,:<>¿?¡!#&$()@%\[\]\{\}\*]{1,500}'                # Regex for credentials validation


def validate_text_value(value: str, regex: str) -> None:
    '''Validate if text value match the allowed regex.

    Args:
        value (str): Text value to be validated
        regex (str): Regex that the value should match

    Raises:
        ValidationError: Raised if value doesn't match the allowed regex
    '''
    if not bool(re.fullmatch(regex, value)):
        logger.warning(f'[Security] Invalid text value that doesn\'t match the regex {regex}')
        raise ValidationError('Value contains unallowed characters')


def validate_number_value(value: int, min: int, max: int) -> None:
    '''Validate if number is in the allowed range.

    Args:
        value (int): Number value to be validated
        min (int): Min allowed value
        max (int): Max allowed value

    Raises:
        ValidationError: Raised if value is not in the allowed range
    '''
    if value < min or value > max:
        logger.warning(f'[Security] Invalid number value {value} that is not in the range {min} - {max}')
        raise ValidationError('Number value is not in the allowed range')


def validate_url(value: str) -> None:
    url = urlparse(value)
    if not url.scheme or not url.netloc:
        logger.warning(f'[Security] Invalid URL value {value}')
        raise ValidationError('URL value is invalid')


def validate_name(value: str) -> None:
    '''Validate if name is valid based on regex.

    Args:
        value (str): Name value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    validate_text_value(value, NAME_REGEX)


def validate_text(value: str) -> None:
    '''Validate if text is valid based on regex.

    Args:
        value (str): Text value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    validate_text_value(value, TEXT_REGEX)


def validate_cve(value: str) -> None:
    '''Validate if path is valid based on regex.

    Args:
        value (str): CVE value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    validate_text_value(value, CVE_REGEX)


def validate_telegram_token(value: str) -> None:
    '''Validate if Telegram token is valid based on regex.

    Args:
        value (str): Telegram token value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    validate_text_value(value, TELEGRAM_TOKEN_REGEX)


def validate_defect_dojo_api_key(value: str) -> None:
    '''Validate if Defect-Dojo API key is valid based on regex.

    Args:
        value (str): Defect-Dojo API key value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    validate_text_value(value, DD_KEY_REGEX)


def validate_credential(value: str) -> None:
    '''Validate if credential is valid based on regex.

    Args:
        value (str): Credential value

    Raises:
        ValidationError: Raised if value doesn't match the expected regex
    '''
    validate_text_value(value, CREDENTIAL_REGEX)


def validate_number(value: int) -> None:
    '''Validate if number is valid based on min and max values.

    Args:
        value (int): Number value

    Raises:
        ValidationError: Raised if value is lower or greater than the expected range
    '''
    validate_number_value(value, 1, 999999)


def validate_time_amount(value: int) -> None:
    '''Validate if specific amount of time is valid based on min and max values.

    Args:
        value (int): Amount of time

    Raises:
        ValidationError: Raised if value is lower or greater than the expected range
    '''
    validate_number_value(value, 1, 1000)


def validate_upload_file_size(value: int) -> None:
    validate_number_value(value, 128, 1024)
