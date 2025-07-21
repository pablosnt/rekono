from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class DefectDojoConfig(BaseApp, AppConfig):
    name = "platforms.defectdojo"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from platforms.defectdojo.models import DefectDojoSettings

        return [DefectDojoSettings]
