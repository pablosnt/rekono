"""Django app configuration for the notes app.

This module defines the Django app configuration for the notes application,
extending the base app configuration with note-specific functionality.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class NotesConfig(BaseApp, AppConfig):
    """Django app configuration for the notes application.

    This configuration class extends both Django's AppConfig and the project's
    BaseApp to provide note-specific functionality and integration with the
    project's base app features.
    """

    name = "notes"
