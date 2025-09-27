"""Django application configuration for mail platform.

Configures the mail platform application with base functionality and
model initialization for SMTP-based email notifications.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class MailConfig(BaseApp, AppConfig):
    """Django application configuration for mail platform.

    Configures the mail platform with SMTP settings model initialization
    and fixture management. Extends BaseApp for consistent application
    configuration across the Rekono platform.

    Attributes:
        name (str): Application name for Django registry
        skip_fixtures_if_model_exists (bool): Skip fixtures if models exist
    """

    name = "platforms.mail"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get list of models for fixture initialization.

        Returns the SMTPSettings model for automatic fixture loading
        during application initialization.

        Returns:
            list[Any]: List containing SMTPSettings model class
        """
        from platforms.mail.models import SMTPSettings

        return [SMTPSettings]
