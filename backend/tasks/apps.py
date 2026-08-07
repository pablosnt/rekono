"""Django app configuration of the tasks app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class TasksConfig(BaseApp, AppConfig):
    """Configuration of the tasks app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "tasks"
