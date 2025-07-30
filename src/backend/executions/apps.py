"""Django app configuration for the executions module.

This module defines the Django app configuration for the executions
application, extending the base app configuration with execution-specific
settings and initialization.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class ExecutionsConfig(BaseApp, AppConfig):
    """Django app configuration for the executions module.

    This class configures the executions Django app, inheriting from
    both BaseApp and Django's AppConfig to provide custom functionality
    while maintaining Django's standard app configuration.

    Attributes:
        name (str): The name of the Django app ('executions').
    """

    name = "executions"
