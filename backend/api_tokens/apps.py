"""Django app configuration of the API tokens app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class ApiTokensConfig(BaseApp, AppConfig):
    """Configuration of the API tokens app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "api_tokens"
