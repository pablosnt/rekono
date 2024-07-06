from pathlib import Path
from typing import Any

from django.apps import AppConfig
from framework.apps import BaseApp


class SettingsConfig(BaseApp, AppConfig):
    name = "settings"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from settings.models import Settings

        return [Settings]
