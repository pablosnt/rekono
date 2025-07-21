from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class MailConfig(BaseApp, AppConfig):
    name = "platforms.mail"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        from platforms.mail.models import SMTPSettings

        return [SMTPSettings]
