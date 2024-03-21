from django.apps import AppConfig

from framework.apps import BaseApp


class FindingsConfig(BaseApp, AppConfig):
    name = "findings"
