"""Django app configuration of the target denylist app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class TargetDenylistConfig(BaseApp, AppConfig):
    """Configuration of the target denylist app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "target_denylist"
