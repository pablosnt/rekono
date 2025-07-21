from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class AlertsConfig(BaseApp, AppConfig):
    name = "alerts"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from alerts.models import MonitorSettings

        return [MonitorSettings]
