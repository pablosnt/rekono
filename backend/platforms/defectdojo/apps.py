"""Django app configuration of the DefectDojo app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class DefectDojoConfig(BaseApp, AppConfig):
    """Configuration of the DefectDojo app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.defectdojo"
