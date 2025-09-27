from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class VirustotalConfig(BaseApp, AppConfig):
    name = "platforms.virustotal"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from platforms.virustotal.models import VirusTotalSettings

        return [VirusTotalSettings]
