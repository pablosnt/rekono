"""Django app configuration of the VirusTotal app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class VirustotalConfig(BaseApp, AppConfig):
    """Configuration of the VirusTotal app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.virustotal"
