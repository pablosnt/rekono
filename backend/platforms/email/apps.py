"""Django app configuration of the email app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class EmailConfig(BaseApp, AppConfig):
    """Configuration of the email app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.email"
