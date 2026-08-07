"""Django app configuration of the stats app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class StatsConfig(BaseApp, AppConfig):
    """Configuration of the stats app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "stats"
