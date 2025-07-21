from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class TelegramAppConfig(BaseApp, AppConfig):
    name = "platforms.telegram_app"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from platforms.telegram_app.models import TelegramSettings

        return [TelegramSettings]
