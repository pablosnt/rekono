"""Django app configuration of the monitor app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class MonitorConfig(BaseApp, AppConfig):
    """Configuration of the monitor app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "monitor"
