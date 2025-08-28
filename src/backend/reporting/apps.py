from django.apps import AppConfig

from framework.apps import BaseApp


class ReportingConfig(BaseApp, AppConfig):
    """Configuration class for the reporting Django application.

    Extends BaseApp and AppConfig to provide reporting-specific
    configuration and integration with Rekono's framework.
    """
    name = "reporting"
