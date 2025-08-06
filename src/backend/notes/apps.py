"""Django application configuration for notes module.

Configures the notes application using the base application framework
for consistent initialization and fixture loading behavior.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class NotesConfig(BaseApp, AppConfig):
    """Configuration class for the notes Django application.

    Extends BaseApp to provide standard application initialization behavior
    for the notes and documentation management system.

    Attributes:
        name (str): The Django application name
    """

    name = "notes"
