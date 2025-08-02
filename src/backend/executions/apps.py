"""Django app configuration for the executions module.

Defines Django app configuration for the executions application with
custom settings and initialization.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class ExecutionsConfig(BaseApp, AppConfig):
    """Django app configuration for the executions module.

    Configures the executions Django app with BaseApp functionality
    and standard Django app configuration.

    Attributes:
        name (str): The name of the Django app
    """

    name = "executions"
