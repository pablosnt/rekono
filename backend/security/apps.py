"""Django application configuration for the security module.

Configures the security application with Django's application framework,
providing initialization and configuration for security components.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class SecurityConfig(BaseApp, AppConfig):
    """Django application configuration for security components.

    Configures the security application within Django's application framework,
    enabling security middleware, authentication backends, and security utilities
    throughout the Rekono platform.

    Attributes:
        name (str): The application name identifier for Django's app registry.
    """

    name = "security"
