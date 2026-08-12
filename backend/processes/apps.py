"""Django app configuration of the processes app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class ProcessesConfig(BaseApp, AppConfig):
    """Configuration of the processes app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "processes"
