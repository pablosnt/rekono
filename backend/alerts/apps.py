"""Django app configuration for the alerts module.

Configures the alerts Django application with BaseApp integration
for consistent framework behavior.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class AlertsConfig(BaseApp, AppConfig):
    """Django app configuration for alerts.

    Configures the alerts Django application with BaseApp functionality
    and standard Django app registration.

    Attributes:
        name (str): The name of the Django app
    """

    name = "alerts"
