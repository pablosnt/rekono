from django.apps import AppConfig

from framework.apps import BaseApp


class ApiTokensConfig(BaseApp, AppConfig):
    name = "api_tokens"
