"""Django application configuration for parameters module.

Configures the parameters application using the base application framework
for consistent initialization and fixture loading behavior.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class ParametersConfig(BaseApp, AppConfig):
    """Configuration class for the parameters Django application.

    Extends BaseApp to provide standard application initialization behavior
    for the input parameters management system.

    Attributes:
        name (str): The Django application name
    """

    name = "parameters"
