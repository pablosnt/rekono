"""Django app configuration of the alerts app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class AlertsConfig(BaseApp, AppConfig):
    """Configuration of the alerts app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "alerts"
