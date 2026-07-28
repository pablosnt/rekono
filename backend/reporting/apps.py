"""Django application configuration for the reporting module.

Registers the reporting application with Rekono's framework, wiring up report
generation and delivery of security assessment results.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class ReportingConfig(BaseApp, AppConfig):
    """Configuration class for the reporting Django application.

    Extends BaseApp and AppConfig to provide reporting-specific
    configuration and integration with Rekono's framework.

    Attributes:
        name (str): The application name identifier for Django registration
    """

    name = "reporting"
