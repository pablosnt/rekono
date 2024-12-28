from pathlib import Path
from typing import Any

from django.apps import AppConfig
from framework.apps import BaseApp


class NvdnistConfig(BaseApp, AppConfig):
    name = "platforms.nvdnist"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from platforms.nvdnist.models import NvdNistSettings

        return [NvdNistSettings]
