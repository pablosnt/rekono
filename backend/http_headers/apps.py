"""Django app configuration of the HTTP headers app."""

from django.apps import AppConfig


class HttpHeadersConfig(AppConfig):
    """Configuration of the HTTP headers app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "http_headers"
