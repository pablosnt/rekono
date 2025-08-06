
"""Django app configuration for HTTP headers module.

Provides app configuration with fixture loading capabilities
for HTTP headers management in the Rekono platform.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class HttpHeadersConfig(BaseApp, AppConfig):
    """Django app configuration for HTTP headers module.

    Inherits from BaseApp to provide automatic fixture loading
    capabilities for initial HTTP header data population.

    Attributes:
        name (str): Django app name identifier
    """

    name = "http_headers"
