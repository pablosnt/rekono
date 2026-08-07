"""Django app configuration of the target ports app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class TargetPortsConfig(BaseApp, AppConfig):
    """Configuration of the target ports app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "target_ports"
