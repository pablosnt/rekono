"""Django app configuration of the reporting app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class ReportingConfig(BaseApp, AppConfig):
    """Configuration of the reporting app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "reporting"
