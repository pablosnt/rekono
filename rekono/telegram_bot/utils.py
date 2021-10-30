from datetime import timedelta

from django.utils import timezone

from rekono.settings import TELEGRAM_TOKEN_EXPIRATION_HOURS


def get_token_expiration():
    return timezone.now() + timedelta(hours=TELEGRAM_TOKEN_EXPIRATION_HOURS)
