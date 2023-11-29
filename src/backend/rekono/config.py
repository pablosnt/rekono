import os
import shutil
import sys
from pathlib import Path
from typing import Any, Optional

import yaml
from cryptography.fernet import Fernet
from rekono.properties import Property


class RekonoConfig:
    def __init__(self) -> None:
        self.testing = "test" in sys.argv
        self.base_dir = Path(__file__).resolve().parent.parent
        self.home = self._get_home()
        self.config_file = self._get_config_file()
        if self.testing:
            self.home = self.base_dir / "tests" / "home"
        self.reports = self.home / "reports"
        self.wordlists = self.home / "wordlists"
        self.logs = self.home / "logs"
        for path in [self.home, self.reports, self.wordlists, self.logs]:
            path.mkdir(exist_ok=True)
        if self.testing:
            shutil.copy(self.config_file, self.home)
            self.config_file = self._get_config_file()
        with self.config_file.open("r") as file:
            self._config_properties = yaml.safe_load(file)
        self.encryption_key = self._get_config(Property.ENCRYPTION_KEY)
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key().decode()
            self._update_config_in_file(
                Property.ENCRYPTION_KEY.value[1], self.encryption_key
            )
        for property in Property:
            if not hasattr(self, property.name.lower()) or not getattr(
                self, property.name.lower()
            ):
                setattr(self, property.name.lower(), self._get_config(property))

    def _get_home(self) -> Path:
        home_from_config = Path(self._get_config(Property.REKONO_HOME))
        return (
            home_from_config
            if home_from_config.is_dir()
            else self.base_dir.parent.parent
        )

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
        properties = self._config_properties
        for key in property.split("."):
            if key not in properties or not properties.get(key):
                return None
            properties = properties.get(key, {})
        return properties

    def _update_config_in_file(self, property: str, value: Any) -> None:
        properties = self._config_properties
        property_path = property.split(".")
        for index, key in enumerate(property_path):
            is_last_path = index + 1 == len(property_path)
            if key not in properties or is_last_path:
                properties[key] = value if is_last_path else {}
            properties = properties[key]
        with self.config_file.open("w") as config_file:
            yaml.dump(self._config_properties, config_file, default_flow_style=False)
