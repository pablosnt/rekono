from django.conf import settings
from django.db import models
from security.otp import get_expiration

# Create your models here.


class TelegramChat(models.Model):
    '''Telegram Chat model.'''

    user = models.OneToOneField(                                                # Linked user account
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telegram_chat',
        blank=True,
        null=True
    )
    chat_id = models.IntegerField(unique=True)                                  # Telegram chat Id
    creation = models.DateTimeField(auto_now_add=True)                          # Telegram chat creation date
    otp = models.TextField(max_length=200, unique=True, blank=True, null=True)  # One Time Password to link user account
    otp_expiration = models.DateTimeField(default=get_expiration, blank=True, null=True)  # OTP expiration date
