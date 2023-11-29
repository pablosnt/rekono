from pathlib import Path
from typing import Any, List

from django.apps import AppConfig
from framework.apps import BaseApp


class TargetBlacklistConfig(BaseApp, AppConfig):
    name = "target_blacklist"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_if_model_exists = True

    def _get_models(self) -> List[Any]:
        from target_blacklist.models import TargetBlacklist

        return [TargetBlacklist]
