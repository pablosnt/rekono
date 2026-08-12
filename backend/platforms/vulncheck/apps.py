"""Django app configuration of the VulnCheck app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class VulncheckConfig(BaseApp, AppConfig):
    """Configuration of the VulnCheck app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.vulncheck"
