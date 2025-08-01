"""Django app configuration for the input_types app.

This module defines the Django app configuration for the input_types
application, extending the base app configuration with input type specific
functionality.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class InputTypesConfig(BaseApp, AppConfig):
    """Django app configuration for the input_types application.

    This configuration class extends both Django's AppConfig and the project's
    BaseApp to provide input type specific functionality and integration with
    the project's base app features.
    """

    name = "input_types"
