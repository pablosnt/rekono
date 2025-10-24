"""Django app configuration for Telegram Bot platform integration.

Configures the Telegram Bot application including fixture management
and model registration for the Rekono platform.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class TelegramAppConfig(BaseApp, AppConfig):
    """Django app configuration for Telegram Bot platform.

    Extends BaseApp with Telegram-specific configuration including
    fixture management and model registration.

    Attributes:
        name (str): The app module path.
        skip_fixtures_if_model_exists (bool): Skip fixtures if models already exist.
    """

    name = "platforms.telegram_app"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get list of models that should exist before loading fixtures.

        Returns:
            list[Any]: List of model classes to check for fixture loading.
        """
        from platforms.telegram_app.models import TelegramSettings

        return [TelegramSettings]
