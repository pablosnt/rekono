from pathlib import Path
from typing import Any, List

from django.apps import AppConfig

from framework.apps import BaseApp


class DefectDojoConfig(BaseApp, AppConfig):
    name = "platforms.defect_dojo"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_if_model_exists = True

    def _get_models(self) -> List[Any]:
        from platforms.defect_dojo.models import DefectDojoSettings

        return [DefectDojoSettings]
