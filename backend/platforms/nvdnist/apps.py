"""Django app configuration of the NVD NIST app."""

from django.apps import AppConfig


class NvdnistConfig(AppConfig):
    """Configuration of the NVD NIST app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "platforms.nvdnist"
