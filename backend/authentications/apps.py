"""Django app configuration of the authentications app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class AuthenticationConfig(BaseApp, AppConfig):
    """Configuration of the authentications app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "authentications"
