"""Django app configuration for targets module.

Configures the targets Django application with base app functionality
and proper application naming for the Django project.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class TargetsConfig(BaseApp, AppConfig):
    """Configuration class for the targets Django application.

    Extends BaseApp to inherit common framework functionality while
    providing application-specific configuration for target management.

    Attributes:
        name (str): The application name used by Django
    """

    name = "targets"
