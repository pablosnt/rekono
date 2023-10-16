from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata


class BaseApp(AppConfig):
    def _load_fixtures(self, **kwargs: Any) -> None:
        path = Path(__file__).resolve().parent / "fixtures"
        management.call_command(
            loaddata.Command(),
            *(path / fixture for fixture in sorted(path.rglob("*.json")))
        )
