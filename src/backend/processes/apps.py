from pathlib import Path
from typing import Any, List

from django.apps import AppConfig
from framework.apps import BaseApp


class ProcessesConfig(BaseApp, AppConfig):
    name = "processes"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_if_model_exists = True

    def _get_models(self) -> List[Any]:
        from processes.models import Process, Step

        return [Process, Step]
