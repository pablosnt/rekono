import os
import shutil
import sys
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

import yaml

from security.cryptography.encryption import Encryptor
from security.cryptography.random import generate_random_value


@dataclass
class Property:
    env: str | None = None
    file: str | None = None
    default: Any = None

    def read(self, file_config: dict[str, Any] = {}) -> Any:
        value = self.default
        if self.env and os.getenv(self.env):
            value = os.getenv(self.env)
            if isinstance(self.default, list):
                list_value = []
                for separator in [" ", ",", ";"]:
                    if separator in value:
                        list_value = value.split(separator)
                        break
                value = list_value or [value]
        elif self.file and file_config:
            found = True
            value_from_file = file_config
            for key in file_config.split("."):
                if key not in file_config:
                    found = False
                    break
                value_from_file = value_from_file.get(key, {})
            if found:
                value = value_from_file
        if isinstance(self.default, bool) and not isinstance(value, bool):
            value = str(value).lower() == "true"
        return value

    def update(self, rekono_config: "RekonoConfig", value: Any) -> dict[str, Any]:
        config = deepcopy(rekono_config.config_from_file)
        config_iterator = config
        property_path = self.file.split(".")
        for index, key in enumerate(property_path):
            is_last_path = index + 1 == len(property_path)
            if key not in config_iterator or is_last_path:
                config_iterator[key] = value if is_last_path else {}
            config_iterator = config_iterator[key]
        with rekono_config.config_file.open("w") as _file:
            yaml.dump(config, _file, default_flow_style=False)


class RekonoConfig:
    testing = "test" in sys.argv
    base_dir = Path(__file__).resolve().parent.parent
    _home = Property("REKONO_HOME", default="/opt/rekono")
    _encryption_key = Property(None, "security.encryption-key", None)
    _pdf_report_template = Property(None, "reports.pdf-template", None)
    _frotend_url = Property("RKN_FRONTEND_URL", "frontend.url", "https://127.0.0.1")
    _root_path = Property("RKN_ROOT_PATH", "rootpath", None)
    _secret_key = Property("RKN_SECRET_KEY", "security.secret-key", generate_random_value(3000))
    _allowed_hosts = Property("RKN_ALLOWED_HOSTS", "security.allowed-hosts", ["localhost", "127.0.0.1", "::1"])
    _trusted_proxy = Property("RKN_TRUSTED_PROXY", None, False)
    _otp_expiration_hours = Property(None, None, 24)
    _mfa_expiration_minutes = Property(None, None, 15)
    _db_name = Property("RKN_DB_NAME", "database.name", "rekono")
    _db_user = Property("RKN_DB_USER", "database.user", "")
    _db_password = Property("RKN_DB_PASSWORD", "database.password", "")
    _db_host = Property("RKN_DB_HOST", "database.host", "127.0.0.1")
    _db_port = Property("RKN_DB_PORT", "database.port", 5432)
    _rq_host = Property("RKN_RQ_HOST", "rq.host", "127.0.0.1")
    _rq_port = Property("RKN_RQ_PORT", "rq.port", 6379)
    _smtp_host = Property("RKN_SMTP_HOST", "email.host", None)
    _smtp_port = Property("RKN_SMTP_PORT", "email.port", 587)
    _smtp_user = Property("RKN_SMTP_USER", "email.user", None)
    _smtp_password = Property("RKN_SMTP_PASSWORD", "email.password", None)
    _smtp_tls = Property("RKN_SMTP_TLS", "email.tls", True)
    _cmseek_dir = Property("RKN_CMSEEK_RESULTS", "tools.cmseek.directory", "/usr/share/cmseek")
    _log4j_scan_dir = Property("RKN_LOG4J_SCAN_DIR", "tools.log4j-scan.directory", "/opt/log4j-scan")
    _spring4shell_scan_dir = Property(
        "RKN_SPRING4SHELL_SCAN_DIR", "tools.spring4shell-scan.directory", "/opt/spring4shell-scan"
    )
    _gittools_dir = Property("RKN_GITTOOLS_DIR", "tools.gittools.directory", "/opt/GitTools")

    @cached_property
    def pro_home(self) -> Path:
        home_value = Path(self._home.read())
        return home_value if home_value.is_dir() else self.base_dir.parent.parent

    @property
    def home(self) -> Path:
        return self._initialize_directory(self.base_dir / "tests" / "home" if self.testing else self.pro_home)

    @cached_property
    def pro_config_file(self) -> Path:
        for filename in [
            "config.yaml",
            "config.yml",
            "rekono.yaml",
            "rekono.yml",
        ]:
            path = self.pro_home / filename
            if path.is_file():
                break
        return path

    @cached_property
    def config_file(self) -> Path:
        if self.testing:
            shutil.copy(self.pro_config_file, self.home)
            return self.home / self.pro_config_file.name
        return self.pro_config_file

    @property
    def config_from_file(self) -> dict[str, Any]:
        with self.config_file.open("r") as file:
            return yaml.safe_load(file)

    @property
    def reports(self) -> Path:
        return self._initialize_directory(self.home / "reports")

    @property
    def generated_reports(self) -> Path:
        return self._initialize_directory(self.reports / "generated")

    @property
    def wordlists(self) -> Path:
        return self._initialize_directory(self.home / "wordlists")

    @property
    def logs(self) -> Path:
        return self._initialize_directory(self.home / "logs")

    @property
    def encryption_key(self) -> str:
        return Encryptor.generate_encryption_key() if self.testing else self._encryption_key.read(self.config_from_file)

    @property
    def pdf_report_template(self) -> Path:
        template = self._pdf_report_template.read(self.config_from_file)
        if template:
            return template
        default_filename = "pdf-report.html"
        for path in [self.home, self.base_dir / "reporting" / "templates"]:
            filepath = path / default_filename
            if filepath.is_file():
                return filepath

    @property
    def frontend_url(self) -> str:
        return self._frotend_url.read(self.config_from_file)

    @property
    def root_path(self) -> str:
        return self._root_path.read(self.config_from_file)

    @property
    def secret_key(self) -> str:
        return self._secret_key.read(self.config_from_file)

    @property
    def allowed_hosts(self) -> list[str]:
        return self._allowed_hosts.read(self.config_from_file)

    @property
    def trusted_proxy(self) -> bool:
        return self._trusted_proxy.read(self.config_from_file)

    @property
    def otp_expiration_hours(self) -> int:
        return self._otp_expiration_hours.read(self.config_from_file)

    @property
    def mfa_expiration_minutes(self) -> int:
        return self._mfa_expiration_minutes.read(self.config_from_file)

    @property
    def db_name(self) -> str:
        return self._db_name.read(self.config_from_file)

    @property
    def db_user(self) -> str:
        return self._db_user.read(self.config_from_file)

    @property
    def db_password(self) -> str:
        return self._db_password.read(self.config_from_file)

    @property
    def db_host(self) -> str:
        return self._db_host.read(self.config_from_file)

    @property
    def db_port(self) -> int:
        return self._db_port.read(self.config_from_file)

    @property
    def rq_host(self) -> str:
        return self._rq_host.read(self.config_from_file)

    @property
    def rq_port(self) -> int:
        return self._rq_port.read(self.config_from_file)

    @property
    def smtp_host(self) -> str:
        return self._smtp_host.read(self.config_from_file)

    @property
    def smtp_port(self) -> int:
        return self._smtp_port.read(self.config_from_file)

    @property
    def smtp_user(self) -> str:
        return self._smtp_user.read(self.config_from_file)

    @property
    def smtp_password(self) -> str:
        return self._smtp_password.read(self.config_from_file)

    @property
    def smtp_tls(self) -> bool:
        return self._smtp_tls.read(self.config_from_file)

    @property
    def cmseek_dir(self) -> str:
        return self._cmseek_dir.read(self.config_from_file)

    @property
    def log4j_scan_dir(self) -> str:
        return self._log4j_scan_dir.read(self.config_from_file)

    @property
    def spring4shell_scan_dir(self) -> str:
        return self._spring4shell_scan_dir.read(self.config_from_file)

    @property
    def gittools_dir(self) -> str:
        return self._gittools_dir.read(self.config_from_file)

    def _initialize_directory(self, path: Path) -> Path:
        path.mkdir(exist_ok=True)
        return path
