"""Django app configuration of the projects app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class ProjectsConfig(BaseApp, AppConfig):
    """Configuration of the projects app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "projects"
