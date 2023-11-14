import os
import sys
from pathlib import Path
from typing import Any, Optional

import yaml
from rekono.properties import Property


class RekonoConfig:
    def __init__(self) -> None:
        self.testing = "test" in sys.argv
        self.base_dir = Path(__file__).resolve().parent.parent
        if self.testing:
            self.home = self.base_dir / "testing" / "home"
        else:
            home_from_config = Path(self._get_config(Property.REKONO_HOME))
            self.home = (
                home_from_config if home_from_config.is_dir() else self.base_dir.parent
            )
        self.reports = self.home / "reports"
        self.wordlists = self.home / "wordlists"
        self.logs = self.home / "logs"
        for path in [self.home, self.reports, self.wordlists, self.logs]:
            path.mkdir(exist_ok=True)
        self.config_file = self._get_config_file()
        with self.config_file.open("r") as file:
            self._config_properties = yaml.safe_load(file)
        for property in Property:
            if not hasattr(self, property.name.lower()) or not getattr(
                self, property.name.lower()
            ):
                setattr(self, property.name.lower(), self._get_config(property))

    def _get_config_file(self) -> Path:
        for filename in [
            "config.yaml",
            "config.yml",
            "rekono.yaml",
            "rekono.yml",
        ]:
            path = self.home / filename
            if path.is_file():
                break
        return path

    def _get_config(self, property: Property) -> Any:
        default_value = value = property.value[2]
        if property.value[1]:
            value = self._get_config_from_file(property.value[1]) or value
        if property.value[0]:
            env_value = os.getenv(property.value[0])
            value = env_value or value
            if isinstance(default_value, list) and env_value:
                list_value = []
                for separator in [" ", ",", ";"]:
                    if separator in env_value:
                        list_value = env_value.split(separator)
                        break
                value = list_value or [env_value]
        if isinstance(default_value, bool) and not isinstance(value, bool):
            value = str(value).lower() == "true"
        return value

    def _get_config_from_file(self, property: str) -> Optional[Any]:
        value = self._config_properties
        for key in property.split("."):
            if key not in value or not value.get(key):
                return None
            value = value.get(key, {})
        return value
