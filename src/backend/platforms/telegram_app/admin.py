"""Django admin configuration for Telegram Bot models.

Registers Telegram Bot models with Django admin interface for
administrative management of settings and chat relationships.
"""

from django.contrib import admin

from platforms.telegram_app.models import TelegramChat, TelegramSettings

admin.site.register(TelegramSettings)
admin.site.register(TelegramChat)
