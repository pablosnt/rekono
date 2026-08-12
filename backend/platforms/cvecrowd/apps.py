"""Django app configuration of the CVE Crowd app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class CvecrowdConfig(BaseApp, AppConfig):
    """Configuration of the CVE Crowd app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.cvecrowd"
