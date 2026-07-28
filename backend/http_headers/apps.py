"""Django app configuration for the http_headers module.

Configures the http_headers Django application with BaseApp integration
for consistent framework behavior.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class HttpHeadersConfig(BaseApp, AppConfig):
    """Configuration class for the http_headers Django application.

    Extends BaseApp to provide standard framework integration for the
    http_headers module with consistent configuration and behavior.

    Attributes:
        name (str): Django app name identifier
    """

    name = "http_headers"
