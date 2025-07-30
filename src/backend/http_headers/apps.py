"""Django app configuration for the http_headers module.

This module defines the Django app configuration for the http_headers
application, extending the base app configuration with HTTP header-specific
settings and initialization.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class HttpHeadersConfig(BaseApp, AppConfig):
    """Django app configuration for the http_headers module.

    This class configures the http_headers Django app, inheriting from
    both BaseApp and Django's AppConfig to provide custom functionality
    while maintaining Django's standard app configuration.

    Attributes:
        name (str): The name of the Django app ('http_headers').
    """

    name = "http_headers"
