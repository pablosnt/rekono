"""Django app configuration of the targets app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class TargetsConfig(BaseApp, AppConfig):
    """Configuration of the targets app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "targets"
