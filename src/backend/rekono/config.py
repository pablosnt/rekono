import os
from pathlib import Path
from typing import Any, List, Optional
from rekono.properties import Property
import sys
import yaml


class RekonoConfig:
    def __init__(self) -> None:
        self.testing = "test" in sys.argv
        self.base_dir = Path(__file__).resolve().parent.parent
        self.home = self._get_home()
        self.reports = os.path.join(self.home, "reports")
        self.wordlists = os.path.join(self.home, "wordlists")
        self.logs = os.path.join(self.home, "logs")
        self._create_missing_directories([self.reports, self.wordlists, self.logs])
        self.config_file = self._get_config_file()
        with open(self.config_file, "r") as file:
            self._config_properties = yaml.safe_load(file)
        self.trusted_proxy = self._get_config(Property.TRUSTED_PROXY).lower() == "true"
        self.allowed_hosts = self._get_allowed_hosts()
        for property in Property:
            if not hasattr(self, property.name.lower()) or not getattr(
                self, property.name.lower()
            ):
                setattr(self, property.name.lower(), self._get_config(property))

    def _get_allowed_hosts(self) -> List[str]:
        hosts = os.getenv(Property.ALLOWED_HOSTS.value[0])
        if hosts:
            if " " in hosts:
                allowed_hosts = hosts.split(" ")
            elif "," in hosts:
                allowed_hosts = hosts.split(",")
            else:
                allowed_hosts = [hosts]
            return allowed_hosts
        return self._get_config(Property.ALLOWED_HOSTS)

    def _get_config_file(self) -> str:
        for filename in [
            "config.yaml",
            "config.yml",
            "rekono.yaml",
            "rekono.yml",
        ]:
            path = os.path.join(self.home, filename)
            if os.path.isfile(path):
                break
        return path

    def _get_home(self) -> str:
        if self.testing:
            home = os.path.join(self.base_dir, "testing", "home")
            self._create_missing_directories([home])
        else:
            home = self._get_config(Property.REKONO_HOME)
            if not os.path.isdir(home):
                home = str(self.base_dir.parent)
        return home

    def _create_missing_directories(self, directories: List[str]) -> None:
        for directory in directories:
            if not os.path.isdir(directory):
                os.mkdir(directory)

    def _get_config(self, property: Property) -> Any:
        value = property.value[2]
        if property.value[1]:
            value = self._get_config_from_file(property.value[1]) or value
        if property.value[0]:
            value = os.getenv(property.name, value)
        return value

    def _get_config_from_file(self, property: str) -> Optional[Any]:
        value = self._config_properties
        for key in property.split("."):
            if key not in value or not value.get(key):
                return None
            value = value.get(key, {})
        return value
