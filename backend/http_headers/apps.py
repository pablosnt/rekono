"""Django app configuration of the HTTP headers app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class HttpHeadersConfig(BaseApp, AppConfig):
    """Configuration of the HTTP headers app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "http_headers"
