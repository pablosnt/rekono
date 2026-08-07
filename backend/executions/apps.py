"""Django app configuration of the executions app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class ExecutionsConfig(BaseApp, AppConfig):
    """Configuration of the executions app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "executions"
