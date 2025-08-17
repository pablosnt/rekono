from django.contrib import admin

from platforms.telegram_app.models import TelegramChat, TelegramSettings

admin.site.register(TelegramSettings)
admin.site.register(TelegramChat)
