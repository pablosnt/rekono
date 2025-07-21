from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class CvecrowdConfig(BaseApp, AppConfig):
    name = "platforms.cvecrowd"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from platforms.cvecrowd.models import CveCrowdSettings

        return [CveCrowdSettings]
