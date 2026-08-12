"""Django app configuration of the wordlists app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class WordlistsConfig(BaseApp, AppConfig):
    """Configuration of the wordlists app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "wordlists"
