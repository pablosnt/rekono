from django.apps import AppConfig

from framework.apps import BaseApp


class NotesConfig(BaseApp, AppConfig):
    name = "notes"