"""Django application configuration for email notification platform.

Configures the email notification platform application with base functionality
and model initialization for SMTP-based email delivery.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class EmailConfig(BaseApp, AppConfig):
    """Configuration class for email notification platform application.

    Extends BaseApp and AppConfig to provide proper Django application setup
    with SMTP settings model registration and fixture management.

    Attributes:
        name (str): Application name for Django registry
        skip_fixtures_if_model_exists (bool): Skip fixtures if models exist
    """

    name = "platforms.email"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get list of models for fixture initialization.

        Returns the SMTPSettings model for automatic fixture loading
        during application initialization.

        Returns:
            list[Any]: List containing SMTPSettings model class
        """
        from platforms.email.models import SMTPSettings

        return [SMTPSettings]
