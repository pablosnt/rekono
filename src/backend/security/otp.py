from datetime import datetime, timedelta

from django.utils import timezone
from security.crypto import generate_random_value, hash

from rekono.settings import OTP_EXPIRATION_HOURS


def generate() -> str:
    '''Generate a secure OTP (One Time Password).

    Returns:
        str: OTP value
    '''
    return hash(generate_random_value(3000))


def get_expiration() -> datetime:
    '''Get expiration datetime for a OTP token.

    Returns:
        datetime: Datetime when the token expires
    '''
    return timezone.now() + timedelta(hours=OTP_EXPIRATION_HOURS)
