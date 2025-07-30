"""Django app configuration for the authentications module.

This module defines the Django app configuration for the authentications
application, extending the base app configuration with authentication-specific
settings and initialization.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class AuthenticationConfig(BaseApp, AppConfig):
    """Django app configuration for the authentications module.

    This class configures the authentications Django app, inheriting from
    both BaseApp and Django's AppConfig to provide custom functionality
    while maintaining Django's standard app configuration.

    Attributes:
        name (str): The name of the Django app ('authentications').
    """

    name = "authentications"
