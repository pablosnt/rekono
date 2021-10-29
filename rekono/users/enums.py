from django.db import models


class Notification(models.TextChoices):
    EMAIL = 'Email'
    TELEGRAM = 'Telegram'

    __empty__ = 'Disabled'
