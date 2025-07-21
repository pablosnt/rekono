from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class TargetDenylistConfig(BaseApp, AppConfig):
    name = "target_denylist"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from target_denylist.models import TargetDenylist

        return [TargetDenylist]
