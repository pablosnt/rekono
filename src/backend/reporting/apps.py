from django.apps import AppConfig

from framework.apps import BaseApp


class ReportingConfig(BaseApp, AppConfig):
    name = "reporting"
