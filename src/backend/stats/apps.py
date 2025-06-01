from django.apps import AppConfig
from framework.apps import BaseApp


class StatsConfig(BaseApp, AppConfig):
    name = "stats"
