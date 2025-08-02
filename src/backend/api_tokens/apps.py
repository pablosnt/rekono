"""App configuration for the api_tokens Django app.

Defines the Django app configuration for the API tokens application.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class ApiTokensConfig(BaseApp, AppConfig):
    """Configuration class for the api_tokens app.

    Configures the API tokens Django application with BaseApp functionality.

    Attributes:
        name (str): The name of the Django app
    """

    name = "api_tokens"
