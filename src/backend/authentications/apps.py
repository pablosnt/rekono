"""Django app configuration for the authentications module.

Defines Django app configuration for the authentications application
with custom settings and initialization.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class AuthenticationConfig(BaseApp, AppConfig):
    """Django app configuration for the authentications module.

    Configures the authentications Django app with BaseApp functionality
    and standard Django app configuration.

    Attributes:
        name (str): The name of the Django app
    """

    name = "authentications"
