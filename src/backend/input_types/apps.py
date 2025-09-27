"""Django app configuration for input_types module.

Contains the Django app configuration for the input_types application,
including base app functionality integration.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class InputTypesConfig(BaseApp, AppConfig):
    """Django app configuration for input_types.

    Configures the input_types Django application with BaseApp functionality.

    Attributes:
        name (str): The name of the Django app.
    """

    name = "input_types"
