from django.apps import AppConfig
from framework.apps import BaseApp


class AuthenticationConfig(BaseApp, AppConfig):
    name = "authentications"
