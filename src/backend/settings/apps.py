from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class SettingsConfig(BaseApp, AppConfig):
    name = "settings"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from settings.models import Settings

        return [Settings]
