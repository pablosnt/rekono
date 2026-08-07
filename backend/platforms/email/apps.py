"""Django app configuration of the email app."""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class EmailConfig(BaseApp, AppConfig):
    """Configuration of the email app.

    Attributes:
        name: Name of the app in the Django app registry.
        skip_fixtures_if_model_exists: The settings are only created once, so the
          configuration of a deployment is never overwritten.
    """

    name = "platforms.email"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the SMTP settings model, whose data comes from the fixtures.

        Returns:
            The SMTP settings model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from platforms.email.models import SMTPSettings

        return [SMTPSettings]
