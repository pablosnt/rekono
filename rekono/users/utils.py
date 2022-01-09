from datetime import timedelta

from django.utils import timezone

from rekono.settings import OTP_TOKEN_EXPIRATION_HOUR


def get_token_expiration():
    return timezone.now() + timedelta(hours=OTP_TOKEN_EXPIRATION_HOUR)
