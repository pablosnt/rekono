"""Django app configuration of the findings app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class FindingsConfig(BaseApp, AppConfig):
    """Configuration of the findings app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "findings"
