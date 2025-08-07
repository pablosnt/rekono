"""Django application configuration for the projects module.

Configures the projects Django application with base functionality and
proper application registration for project management features.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class ProjectsConfig(BaseApp, AppConfig):
    """Django application configuration for projects module.

    Extends BaseApp to provide standardized Rekono application configuration
    with integrated logging and framework features for project management.

    Attributes:
        name (str): The application name identifier for Django registration
    """

    name = "projects"
