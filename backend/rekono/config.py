"""Configuration management for the Rekono platform.

Every configurable value is declared as a Property that resolves, in order, from an
environment variable, the YAML configuration file, and a hardcoded default. Paths
exposed here are created on access, and the whole configuration switches to an
isolated directory tree when running the test suite.
"""

import os
import shutil
import sys
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from security.cryptography import Crypto


@dataclass
class Property:
    """A configuration value and the sources it can be read from.

    Attributes:
        env: Environment variable name, or None if the value can't be set that way.
        file: Dot-separated path in the configuration file, like "database.host".
        default: Value used when no source provides one. Its type also drives the
          conversion applied to values read from the environment.
    """

    env: str | None = None
    file: str | None = None
    default: Any = None

    def read(self, file_config: dict[str, Any] = {}) -> Any:
        """Read the property value from its sources.

        Sources are applied in order of precedence: environment variable, then
        configuration file, then default value.

        A key that is present in the configuration file but explicitly set to null is
        treated the same as a missing key: the value falls through to the default
        instead of resolving to None. Combined with ``update``, this is what lets a
        property such as the encryption key be cleared by writing null to the file.

        Environment variables are always strings, so the value is converted to the type
        of the default: booleans, integers, and lists split on a common separator.
        Values that can't be converted fall back to the default instead of raising.

        Args:
            file_config: Parsed contents of the configuration file.

        Returns:
            The resolved value, converted to the type of the default.
        """
        value = self.default
        env_value = os.getenv(self.env) if self.env else None
        if env_value:
            value = env_value
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
            for key in self.file.split("."):
                if key not in value_from_file:
                    found = False
                    break
                value_from_file = value_from_file.get(key, {})
            if found and value_from_file is not None:
                value = value_from_file
        if isinstance(self.default, bool) and not isinstance(value, bool):
            value = str(value).lower() == "true"
        # After the bool check, since bool is a subclass of int
        elif isinstance(self.default, int) and not isinstance(value, int):
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = self.default
        return value

    def update(self, rekono_config: "RekonoConfig", value: Any) -> None:
        """Write a new value for this property to the configuration file.

        The rest of the file is preserved, and the nested dictionaries along the
        property path are created if they don't exist yet.

        Passing None as value writes an explicit null rather than removing the key.
        Since ``read`` treats a null file value the same as a missing one, this is how
        the encryption key is cleared: calling ``update`` with None makes the next
        ``read`` fall back to its default of None instead of returning the old key.

        Args:
            rekono_config: Configuration manager that locates the file to update.
            value: Value to store, or None to clear the property.
        """
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
    """Configuration of all the Rekono subsystems.

    Groups the properties for the database, the Redis queues, the frontend, the
    security settings, and the third party tools that Rekono executes. In testing
    mode it works on an isolated home directory and a throwaway encryption key, so
    the test suite never reads or writes the real deployment configuration.

    Attributes:
        testing: Whether Rekono is running the test suite.
        base_dir: Root directory of the backend source code.
    """

    testing = "test" in sys.argv
    base_dir = Path(__file__).resolve().parent.parent
    _home = Property("REKONO_HOME", default="/opt/rekono")
    _db_name = Property("RKN_DB_NAME", "database.name", "rekono")
    _db_user = Property("RKN_DB_USER", "database.user", "")
    _db_password = Property("RKN_DB_PASSWORD", "database.password", "")
    _db_host = Property("RKN_DB_HOST", "database.host", "127.0.0.1")
    _db_port = Property("RKN_DB_PORT", "database.port", 5432)
    _rq_host = Property("RKN_RQ_HOST", "rq.host", "127.0.0.1")
    _rq_port = Property("RKN_RQ_PORT", "rq.port", 6379)
    _frontend_url = Property("RKN_FRONTEND_URL", "frontend.url", "https://127.0.0.1")
    _frontend_desktop = Property("RKN_FRONTEND_DESKTOP", "frontend.desktop", False)
    _trusted_proxies = Property("RKN_TRUSTED_PROXIES", None, 0)
    _allowed_hosts = Property("RKN_ALLOWED_HOSTS", "security.allowed-hosts", ["localhost", "127.0.0.1", "::1"])
    _encryption_key = Property(None, "security.encryption-key", None)
    _secret_key = Property("RKN_SECRET_KEY", "security.secret-key", Crypto.random(3000))
    _secure_cookies = Property("RKN_COOKIES_SECURE", "security.cookies.secure", False)
    _otp_expiration_hours = Property(None, None, 24)
    _mfa_expiration_minutes = Property(None, None, 15)
    _pdf_report_template = Property(None, "reports.pdf-template", None)
    _cmseek_dir = Property("RKN_CMSEEK_RESULTS", "tools.cmseek.directory", "/usr/share/cmseek")
    _log4j_scan_dir = Property("RKN_LOG4J_SCAN_DIR", "tools.log4j-scan.directory", "/opt/log4j-scan")
    _spring4shell_scan_dir = Property(
        "RKN_SPRING4SHELL_SCAN_DIR",
        "tools.spring4shell-scan.directory",
        "/opt/spring4shell-scan",
    )
    _emailharvester_dir = Property("RKN_EMAILHARVESTER_DIR", "tools.emailharvester.directory", "/opt/EmailHarvester")
    _gittools_dir = Property("RKN_GITTOOLS_DIR", "tools.gittools.directory", "/opt/GitTools")

    @cached_property
    def pro_home(self) -> Path:
        """The configured home directory, or the parent of the backend if it's missing."""
        home_value = Path(self._home.read())
        return home_value if home_value.is_dir() else self.base_dir.parent

    @property
    def home(self) -> Path:
        """The home directory in use, created if needed and isolated during testing."""
        return self._initialize_directory(self.base_dir / "tests" / "home" if self.testing else self.pro_home)

    @cached_property
    def pro_config_file(self) -> Path:
        """The first supported configuration filename found in the production home.

        When none of them exists, the last candidate is returned anyway, so callers
        that only read the configuration get a path pointing to a missing file.
        """
        for filename in ["config.yaml", "config.yml", "rekono.yaml", "rekono.yml"]:
            path = self.pro_home / filename
            if path.is_file():
                break
        return path

    @cached_property
    def config_file(self) -> Path:
        """The configuration file in use, a copy in the test home during testing."""
        if self.testing:
            shutil.copy(self.pro_config_file, self.home)
            return self.home / self.pro_config_file.name
        return self.pro_config_file

    @property
    def config_from_file(self) -> dict[str, Any]:
        """The parsed contents of the configuration file.

        Not cached: the file is re-read and re-parsed on every access, so a value
        written by ``Property.update`` is visible to the very next ``Property.read``
        without needing to restart the process.
        """
        with self.config_file.open("r") as file:
            return yaml.safe_load(file)

    @property
    def reports(self) -> Path:
        """The directory where the reports are stored, created if needed."""
        return self._initialize_directory(self.home / "reports")

    @property
    def generated_reports(self) -> Path:
        """The directory where the generated reports are stored, created if needed."""
        return self._initialize_directory(self.reports / "generated")

    @property
    def wordlists(self) -> Path:
        """The directory where the wordlists are stored, created if needed."""
        return self._initialize_directory(self.home / "wordlists")

    @property
    def logs(self) -> Path:
        """The directory where the log files are written, created if needed."""
        return self._initialize_directory(self.home / "logs")

    @property
    def encryption_key(self) -> str | None:
        """The key used to encrypt sensitive data, or None if it's not configured yet.

        A random key is generated on every access in testing mode, rather than read
        from the configuration file, so tests never depend on a real encryption key
        being configured.
        """
        return Crypto.generate_encryption_key() if self.testing else self._encryption_key.read(self.config_from_file)

    @property
    def pdf_report_template(self) -> Path | None:
        """The HTML template used to generate PDF reports.

        Falls back to the default template in the home directory or in the reporting
        app, and is None when no template is available at all.
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
        """The base URL of the Rekono frontend, without trailing slash.

        The URL may include a path component when the frontend is exposed under
        a root path by a reverse proxy (e.g. ``https://localhost/rekono``). Any
        trailing slash is removed so links can be built as ``{frontend_url}/...``.
        """
        return str(self._frontend_url.read(self.config_from_file)).rstrip("/")

    @property
    def frontend_origin(self) -> str:
        """The frontend origin (scheme and host) without any path.

        Used for CORS headers, which must reference an origin rather than a full
        URL with a path component.
        """
        parsed = urlparse(self.frontend_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    @property
    def frontend_desktop(self) -> bool:
        """Whether the frontend is deployed as a desktop application.

        Cookies are then shared across the app origin, so the SameSite policy is
        relaxed to None.
        """
        return self._frontend_desktop.read(self.config_from_file)

    @property
    def root_path(self) -> str:
        """The path prefix where Rekono is exposed, or an empty string.

        The root path is derived from the path component of the frontend URL,
        since the frontend and backend are expected to be exposed under the same
        prefix by a reverse proxy. A frontend URL without a path (or with just
        ``/``) means no root path. The result is normalized with a leading slash
        and without a trailing slash.
        """
        path = urlparse(self.frontend_url).path.strip("/")
        return f"/{path}" if path else ""

    @property
    def secret_key(self) -> str:
        """The Django secret key, randomly generated if it's not configured."""
        return self._secret_key.read(self.config_from_file)

    @property
    def secure_cookies(self) -> bool:
        """Whether the ``Secure`` flag should be set in the authentication cookies."""
        return self._secure_cookies.read(self.config_from_file)

    @property
    def allowed_hosts(self) -> list[str]:
        """The host names that Rekono accepts requests for."""
        return self._allowed_hosts.read(self.config_from_file)

    @property
    def trusted_proxies(self) -> int:
        """The number of trusted proxies deployed in front of Rekono.

        It's the number of entries that these proxies append to the X-Forwarded-For
        header, so the client IP address can be resolved from the header ignoring the
        entries that the client supplied itself.
        """
        return self._trusted_proxies.read(self.config_from_file)

    @property
    def otp_expiration_hours(self) -> int:
        """The number of hours before the one time passwords expire."""
        return self._otp_expiration_hours.read(self.config_from_file)

    @property
    def mfa_expiration_minutes(self) -> int:
        """The number of minutes before the MFA codes expire."""
        return self._mfa_expiration_minutes.read(self.config_from_file)

    @property
    def db_name(self) -> str:
        """The name of the PostgreSQL database."""
        return self._db_name.read(self.config_from_file)

    @property
    def db_user(self) -> str:
        """The user to authenticate against the PostgreSQL database."""
        return self._db_user.read(self.config_from_file)

    @property
    def db_password(self) -> str:
        """The password to authenticate against the PostgreSQL database."""
        return self._db_password.read(self.config_from_file)

    @property
    def db_host(self) -> str:
        """The host where the PostgreSQL database is deployed."""
        return self._db_host.read(self.config_from_file)

    @property
    def db_port(self) -> int:
        """The port where the PostgreSQL database is listening."""
        return self._db_port.read(self.config_from_file)

    @property
    def rq_host(self) -> str:
        """The host where the Redis server used by the job queues is deployed."""
        return self._rq_host.read(self.config_from_file)

    @property
    def rq_port(self) -> int:
        """The port where the Redis server used by the job queues is listening."""
        return self._rq_port.read(self.config_from_file)

    @property
    def cmseek_dir(self) -> str:
        """The directory where CMSeek is installed and writes its reports."""
        return self._cmseek_dir.read(self.config_from_file)

    @property
    def log4j_scan_dir(self) -> str:
        """The directory where log4j-scan is installed."""
        return self._log4j_scan_dir.read(self.config_from_file)

    @property
    def spring4shell_scan_dir(self) -> str:
        """The directory where spring4shell-scan is installed."""
        return self._spring4shell_scan_dir.read(self.config_from_file)

    @property
    def emailharvester_dir(self) -> str:
        """The directory where EmailHarvester is installed."""
        return self._emailharvester_dir.read(self.config_from_file)

    @property
    def gittools_dir(self) -> str:
        """The directory where GitTools is installed."""
        return self._gittools_dir.read(self.config_from_file)

    def _initialize_directory(self, path: Path) -> Path:
        """Create the directory if it doesn't exist and return its path.

        Args:
            path: Directory to create, whose parents must already exist.

        Returns:
            The same path, so it can be assigned directly by the caller.
        """
        path.mkdir(exist_ok=True)
        return path
