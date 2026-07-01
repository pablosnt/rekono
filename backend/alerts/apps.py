"""Django app configuration for alerts module.

Contains the Django app configuration for the alerts application,
including model registration and fixture handling.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class AlertsConfig(BaseApp, AppConfig):
    """Django app configuration for alerts.

    Configures the alerts Django application with model registration
    and fixture loading behavior.

    Attributes:
        name (str): The name of the Django app
    """

    name = "alerts"
