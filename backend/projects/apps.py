"""Django app configuration for the projects module.

Configures the projects Django application with BaseApp integration
for consistent framework behavior.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class ProjectsConfig(BaseApp, AppConfig):
    """Configuration class for the projects Django application.

    Extends BaseApp to provide standard framework integration for the
    projects module with consistent configuration and behavior.

    Attributes:
        name (str): The name of the Django application
    """

    name = "projects"
