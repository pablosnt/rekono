from pathlib import Path

from django.apps import AppConfig
from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    name = "integrations"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
