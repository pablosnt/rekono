"""Django app configuration for target ports module.

Configures the target_ports Django application with base app functionality
and proper application naming for the Django project.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class TargetPortsConfig(BaseApp, AppConfig):
    """Configuration class for the target_ports Django application.

    Extends BaseApp to inherit common framework functionality while
    providing application-specific configuration for target port management.

    Attributes:
        name (str): The application name used by Django
    """

    name = "target_ports"
