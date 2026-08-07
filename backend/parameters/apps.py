"""Django app configuration of the parameters app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class ParametersConfig(BaseApp, AppConfig):
    """Configuration of the parameters app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "parameters"
