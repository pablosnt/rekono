from django.contrib import admin
from platforms.telegram_app.models import TelegramChat, TelegramSettings

# Register your models here.

admin.site.register(TelegramSettings)
admin.site.register(TelegramChat)
