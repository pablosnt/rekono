from datetime import datetime, timedelta

from django.utils import timezone

from rekono.settings import OTP_EXPIRATION_HOURS


def get_expiration() -> datetime:
    '''Get expiration datetime for a OTP token.

    Returns:
        datetime: Datetime when the token expires
    '''
    return timezone.now() + timedelta(hours=OTP_EXPIRATION_HOURS)
