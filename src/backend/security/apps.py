from django.apps import AppConfig

from framework.apps import BaseApp


class SecurityConfig(BaseApp, AppConfig):
    name = "security"
