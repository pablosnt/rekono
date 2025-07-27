"""
Rekono configuration management.

Configuration management for the Rekono platform, including environment
variable handling, YAML config file parsing, and property management for
application settings.
"""

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
    """
    Rekono configuration property.

    Represents a configuration property that can be loaded from environment
    variables, files, or defaults.

    Attributes:
        env (str | None): The environment variable name.
        file (str | None): The dot-separated path in the config file.
        default (Any): The default value if not set elsewhere.
    """

    env: str | None = None
    file: str | None = None
    default: Any = None

    def read(self, file_config: dict[str, Any] = {}) -> Any:
        """
        Read the property value from environment, file, or default.

        Args:
            file_config (dict[str, Any]): The configuration loaded from file.

        Returns:
            Any: The resolved property value.
        """
        # Priority: environment variable > config file > default value
        value = self.default
        if self.env and os.getenv(self.env):
            value = os.getenv(self.env)
            # If the default is a list, try to split the env value using common
            # separators
            if isinstance(self.default, list):
                list_value = []
                for separator in [" ", ",", ";"]:
                    if separator in value:
                        list_value = value.split(separator)
                        break
                value = list_value or [value]
        elif self.file and file_config:
            # Traverse nested config dict using dot-separated path
            found = True
            value_from_file = file_config
            for key in file_config.split("."):
                if key not in file_config:
                    found = False
                    break
                value_from_file = value_from_file.get(key, {})
            if found:
                value = value_from_file
        # Convert to bool if needed
        if isinstance(self.default, bool) and not isinstance(value, bool):
            value = str(value).lower() == "true"
        return value

    def update(self, rekono_config: "RekonoConfig", value: Any) -> dict[str, Any]:
        """
        Update the property value in the Rekono config file.

        Args:
            rekono_config (RekonoConfig): The RekonoConfig instance.
            value (Any): The new value to set.

        Returns:
            dict[str, Any]: The updated configuration dictionary.
        """
        # Deep copy the config to avoid mutating the original
        config = deepcopy(rekono_config.config_from_file)
        config_iterator = config
        property_path = self.file.split(".")
        for index, key in enumerate(property_path):
            is_last_path = index + 1 == len(property_path)
            # Traverse or create nested dictionaries as needed
            if key not in config_iterator or is_last_path:
                config_iterator[key] = value if is_last_path else {}
            config_iterator = config_iterator[key]
        # Write the updated config back to YAML
        with rekono_config.config_file.open("w") as _file:
            yaml.dump(config, _file, default_flow_style=False)


class RekonoConfig:
    """
    Main configuration handler for the Rekono platform.

    Loads and manages all application settings, YAML config files, and default values.
    """

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
        """
        Returns the Rekono home directory path.

        Returns:
            Path: The home directory path.
        """
        # Use the environment or config value if it exists and is a directory,
        # otherwise fall back to the parent of the backend directory
        home_value = Path(self._home.read())
        return home_value if home_value.is_dir() else self.base_dir.parent.parent

    @property
    def home(self) -> Path:
        """
        Returns the working home directory, using a test directory if in testing mode.

        Returns:
            Path: The working home directory.
        """
        # In test mode, use a dedicated test home directory
        return self._initialize_directory(self.base_dir / "tests" / "home" if self.testing else self.pro_home)

    @cached_property
    def pro_config_file(self) -> Path:
        """
        Finds and returns the main Rekono config file path.

        Returns:
            Path: The config file path.
        """
        # Search for the first config file that exists in the home directory
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
        """
        Returns the config file path, copying to a test location if in testing mode.

        Returns:
            Path: The config file path.
        """
        # In test mode, copy the config file to the test home directory
        if self.testing:
            shutil.copy(self.pro_config_file, self.home)
            return self.home / self.pro_config_file.name
        return self.pro_config_file

    @property
    def config_from_file(self) -> dict[str, Any]:
        """
        Loads and returns the configuration from the YAML config file.

        Returns:
            dict[str, Any]: The loaded configuration dictionary.
        """
        # Loads YAML from disk every time this property is accessed
        with self.config_file.open("r") as file:
            return yaml.safe_load(file)

    @property
    def reports(self) -> Path:
        """
        Returns the reports directory path, creating it if necessary.

        Returns:
            Path: The reports directory path.
        """
        # Ensure the reports directory exists
        return self._initialize_directory(self.home / "reports")

    @property
    def generated_reports(self) -> Path:
        """
        Returns the generated reports directory path, creating it if necessary.

        Returns:
            Path: The generated reports directory path.
        """
        # Ensure the generated reports directory exists
        return self._initialize_directory(self.reports / "generated")

    @property
    def wordlists(self) -> Path:
        """
        Returns the wordlists directory path, creating it if necessary.

        Returns:
            Path: The wordlists directory path.
        """
        # Ensure the wordlists directory exists
        return self._initialize_directory(self.home / "wordlists")

    @property
    def logs(self) -> Path:
        """
        Returns the logs directory path, creating it if necessary.

        Returns:
            Path: The logs directory path.
        """
        # Ensure the logs directory exists
        return self._initialize_directory(self.home / "logs")

    @property
    def encryption_key(self) -> str:
        """
        Returns the encryption key, generating a new one if in testing mode.

        Returns:
            str: The encryption key.
        """
        return Encryptor.generate_encryption_key() if self.testing else self._encryption_key.read(self.config_from_file)

    @property
    def pdf_report_template(self) -> Path:
        """
        Returns the path to the PDF report template.

        Returns:
            Path: The PDF report template path.
        """
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
        """
        Returns the frontend URL.

        Returns:
            str: The frontend URL.
        """
        return self._frotend_url.read(self.config_from_file)

    @property
    def root_path(self) -> str:
        """
        Returns the root path for the application.

        Returns:
            str: The root path.
        """
        return self._root_path.read(self.config_from_file)

    @property
    def secret_key(self) -> str:
        """
        Returns the secret key for the application.

        Returns:
            str: The secret key.
        """
        return self._secret_key.read(self.config_from_file)

    @property
    def allowed_hosts(self) -> list[str]:
        """
        Returns the list of allowed hosts.

        Returns:
            list[str]: The allowed hosts.
        """
        return self._allowed_hosts.read(self.config_from_file)

    @property
    def trusted_proxy(self) -> bool:
        """
        Returns whether a trusted proxy is enabled.

        Returns:
            bool: True if trusted proxy is enabled, else False.
        """
        return self._trusted_proxy.read(self.config_from_file)

    @property
    def otp_expiration_hours(self) -> int:
        """
        Returns the OTP expiration time in hours.

        Returns:
            int: OTP expiration in hours.
        """
        return self._otp_expiration_hours.read(self.config_from_file)

    @property
    def mfa_expiration_minutes(self) -> int:
        """
        Returns the MFA expiration time in minutes.

        Returns:
            int: MFA expiration in minutes.
        """
        return self._mfa_expiration_minutes.read(self.config_from_file)

    @property
    def db_name(self) -> str:
        """
        Returns the database name.

        Returns:
            str: The database name.
        """
        return self._db_name.read(self.config_from_file)

    @property
    def db_user(self) -> str:
        """
        Returns the database user.

        Returns:
            str: The database user.
        """
        return self._db_user.read(self.config_from_file)

    @property
    def db_password(self) -> str:
        """
        Returns the database password.

        Returns:
            str: The database password.
        """
        return self._db_password.read(self.config_from_file)

    @property
    def db_host(self) -> str:
        """
        Returns the database host.

        Returns:
            str: The database host.
        """
        return self._db_host.read(self.config_from_file)

    @property
    def db_port(self) -> int:
        """
        Returns the database port.

        Returns:
            int: The database port.
        """
        return self._db_port.read(self.config_from_file)

    @property
    def rq_host(self) -> str:
        """
        Returns the Redis queue host.

        Returns:
            str: The Redis queue host.
        """
        return self._rq_host.read(self.config_from_file)

    @property
    def rq_port(self) -> int:
        """
        Returns the Redis queue port.

        Returns:
            int: The Redis queue port.
        """
        return self._rq_port.read(self.config_from_file)

    @property
    def smtp_host(self) -> str:
        """
        Returns the SMTP host.

        Returns:
            str: The SMTP host.
        """
        return self._smtp_host.read(self.config_from_file)

    @property
    def smtp_port(self) -> int:
        """
        Returns the SMTP port.

        Returns:
            int: The SMTP port.
        """
        return self._smtp_port.read(self.config_from_file)

    @property
    def smtp_user(self) -> str:
        """
        Returns the SMTP user.

        Returns:
            str: The SMTP user.
        """
        return self._smtp_user.read(self.config_from_file)

    @property
    def smtp_password(self) -> str:
        """
        Returns the SMTP password.

        Returns:
            str: The SMTP password.
        """
        return self._smtp_password.read(self.config_from_file)

    @property
    def smtp_tls(self) -> bool:
        """
        Returns whether SMTP TLS is enabled.

        Returns:
            bool: True if SMTP TLS is enabled, else False.
        """
        return self._smtp_tls.read(self.config_from_file)

    @property
    def cmseek_dir(self) -> str:
        """
        Returns the directory for CMSeek tool results.

        Returns:
            str: The CMSeek directory.
        """
        return self._cmseek_dir.read(self.config_from_file)

    @property
    def log4j_scan_dir(self) -> str:
        """
        Returns the directory for Log4j scan tool.

        Returns:
            str: The Log4j scan directory.
        """
        return self._log4j_scan_dir.read(self.config_from_file)

    @property
    def spring4shell_scan_dir(self) -> str:
        """
        Returns the directory for Spring4Shell scan tool.

        Returns:
            str: The Spring4Shell scan directory.
        """
        return self._spring4shell_scan_dir.read(self.config_from_file)

    @property
    def gittools_dir(self) -> str:
        """
        Returns the directory for GitTools.

        Returns:
            str: The GitTools directory.
        """
        return self._gittools_dir.read(self.config_from_file)

    def _initialize_directory(self, path: Path) -> Path:
        """
        Ensure the directory exists at the given path.

        Args:
            path (Path): The directory path to initialize.

        Returns:
            Path: The initialized directory path.
        """
        # Create the directory if it does not exist
        path.mkdir(exist_ok=True)
        return path
