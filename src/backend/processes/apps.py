from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class ProcessesConfig(BaseApp, AppConfig):
    name = "processes"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from processes.models import Process, Step

        return [Process, Step]
