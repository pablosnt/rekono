"""Django app configuration of the Telegram app."""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class TelegramAppConfig(BaseApp, AppConfig):
    """Configuration of the Telegram app.

    Attributes:
        name: Name of the app in the Django app registry.
        skip_fixtures_if_model_exists: The settings are only created once, so the
          configuration of a deployment is never overwritten.
    """

    name = "platforms.telegram_app"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the Telegram settings model, whose data comes from the fixtures.

        Returns:
            The Telegram settings model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from platforms.telegram_app.models import TelegramSettings

        return [TelegramSettings]
