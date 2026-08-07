"""Django app configuration of the input types app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class InputTypesConfig(BaseApp, AppConfig):
    """Configuration of the input types app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "input_types"
