from pathlib import Path
from typing import Any, List

from django.apps import AppConfig
from framework.apps import BaseApp


class SettingsConfig(BaseApp, AppConfig):
    name = "settings"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_if_model_exists = True

    def _get_models(self) -> List[Any]:
        from settings.models import Settings

        return [Settings]

    def _load_fixtures(self, **kwargs: Any) -> None:
        from settings.models import Settings

        if Settings.objects.exists():
            return
        return super()._load_fixtures(**kwargs)
