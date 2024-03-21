from django.apps import AppConfig

from framework.apps import BaseApp


class ProjectsConfig(BaseApp, AppConfig):
    name = "projects"
