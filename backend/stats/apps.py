"""Django app configuration for the stats module.

Configures the stats Django application with BaseApp integration
for consistent framework behavior.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class StatsConfig(BaseApp, AppConfig):
    """Django app configuration for statistics and analytics.

    Configures the stats Django application with BaseApp functionality
    and standard Django app registration.

    Attributes:
        name (str): The name of the Django app
    """

    name = "stats"
