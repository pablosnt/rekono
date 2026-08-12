"""Django app configuration of the security app."""

from django.apps import AppConfig


class SecurityConfig(AppConfig):
    """Configuration of the security app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "security"

    def ready(self) -> None:
        """Register the OpenAPI extension that documents the JWT cookie scheme.

        The import must happen here rather than at module level to ensure the
        app registry is fully populated before drf-spectacular introspects it.
        """
        super().ready()
        import security.authentication.openapi  # noqa: F401
