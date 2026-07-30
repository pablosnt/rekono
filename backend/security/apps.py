"""Django application configuration for the security module.

Registers the security app with Django's application framework and, once the
app registry is ready, imports the OpenAPI extension that documents the
cookie-based JWT authentication scheme for drf-spectacular.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class SecurityConfig(BaseApp, AppConfig):
    """Configuration class for the security Django application.

    Extends BaseApp and AppConfig to provide standard framework integration,
    plus a custom ready() hook that registers CookieJWTAuthenticationScheme
    with drf-spectacular's OpenAPI schema generation.

    Attributes:
        name (str): The application name identifier for Django's app registry.
    """

    name = "security"

    def ready(self) -> None:
        """Initialize the security application after the app registry is loaded.

        Calls the base class setup and then imports the OpenAPI extension
        module so that drf-spectacular discovers CookieJWTAuthenticationScheme.
        The import must happen here rather than at module level to ensure the
        app registry is fully populated before drf-spectacular introspects it.
        """
        super().ready()
        import security.authentication.openapi  # noqa: F401
