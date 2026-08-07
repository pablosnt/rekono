"""Registration of the Telegram models in the Django admin site."""

from django.contrib import admin

from platforms.telegram_app.models import TelegramChat, TelegramSettings

admin.site.register(TelegramSettings)
admin.site.register(TelegramChat)
