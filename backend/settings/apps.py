"""Django app configuration of the settings app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class SettingsConfig(BaseApp, AppConfig):
    """Configuration of the settings app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "settings"
