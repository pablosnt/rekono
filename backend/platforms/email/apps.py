"""Django app configuration of the email app."""

from django.apps import AppConfig


class EmailConfig(AppConfig):
    """Configuration of the email app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.email"
