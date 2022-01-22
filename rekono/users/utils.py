from datetime import datetime, timedelta

from django.utils import timezone

from rekono.settings import OTP_TOKEN_EXPIRATION_HOUR


def get_token_expiration() -> datetime:
    '''Get expiration datetime for a OTP token.

    Returns:
        datetime: Datetime when the token expires
    '''
    return timezone.now() + timedelta(hours=OTP_TOKEN_EXPIRATION_HOUR)
