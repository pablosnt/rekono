"""Django app configuration of the NVD NIST app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class NvdnistConfig(BaseApp, AppConfig):
    """Configuration of the NVD NIST app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.nvdnist"
