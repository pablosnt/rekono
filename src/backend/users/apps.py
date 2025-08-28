from django.apps import AppConfig

from framework.apps import BaseApp


class UsersConfig(BaseApp, AppConfig):
    name = "users"
