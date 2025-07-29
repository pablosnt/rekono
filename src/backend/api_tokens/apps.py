"""App configuration for the api_tokens Django app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class ApiTokensConfig(BaseApp, AppConfig):
    """Configuration class for the api_tokens app."""

    name = "api_tokens"
