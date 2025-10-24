"""Django app configuration for the tasks module.

Configures the tasks Django application with BaseApp integration
for consistent framework behavior.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class TasksConfig(BaseApp, AppConfig):
    """Configuration class for the tasks Django application.

    Extends BaseApp to provide standard framework integration for the
    tasks module with consistent configuration and behavior.

    Attributes:
        name (str): The name of the Django application
    """

    name = "tasks"
