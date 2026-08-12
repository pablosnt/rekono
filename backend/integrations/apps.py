"""Django app configuration of the integrations app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    """Configuration of the integrations app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "integrations"
