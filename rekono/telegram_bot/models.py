from django.db import models
from telegram_bot.utils import get_token_expiration

# Create your models here.


class TelegramChat(models.Model):
    chat_id = models.IntegerField(unique=True)
    start_token = models.TextField(max_length=200, unique=True)
    creation = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(default=get_token_expiration)
