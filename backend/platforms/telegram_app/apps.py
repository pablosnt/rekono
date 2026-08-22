"""Django app configuration of the Telegram app."""

from django.apps import AppConfig


class TelegramAppConfig(AppConfig):
    """Configuration of the Telegram app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.telegram_app"
