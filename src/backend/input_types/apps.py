from pathlib import Path

from django.apps import AppConfig

from framework.apps import BaseApp


class InputTypesConfig(BaseApp, AppConfig):
    name = "input_types"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
