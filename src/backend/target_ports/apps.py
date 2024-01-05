from django.apps import AppConfig

from framework.apps import BaseApp


class TargetPortsConfig(BaseApp, AppConfig):
    name = "target_ports"
