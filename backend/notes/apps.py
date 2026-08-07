"""Django app configuration of the notes app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class NotesConfig(BaseApp, AppConfig):
    """Configuration of the notes app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "notes"
