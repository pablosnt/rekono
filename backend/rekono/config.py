"""Configuration management system for Rekono platform.

This module provides a comprehensive configuration management system that supports
multiple configuration sources including environment variables, YAML files, and
default values with intelligent precedence handling and validation.

The system manages all aspects of Rekono configuration including database connections,
security settings, external service integrations, file system paths, and tool-specific
parameters with automatic directory initialization and type conversion.
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
    """Configuration property with multiple source support.

    Represents a single configuration property that can be sourced from
    environment variables, configuration files, or default values with
    intelligent type conversion and precedence handling.

    Attributes:
        env (str | None): Environment variable name for this property.
        file (str | None): Dot-separated path in configuration file (e.g., 'database.host').
        default (Any): Default value when no other sources are available.

    Example:
        Create a database host property:

        ```python
        db_host = Property(
            env="RKN_DB_HOST",
            file="database.host",
            default="127.0.0.1"
        )
        ```
    """

    env: str | None = None
    file: str | None = None
    default: Any = None

    def read(self, file_config: dict[str, Any] = {}) -> Any:
        """Read property value from configured sources.

        Resolves the property value using the following precedence:
        1. Environment variable (highest priority)
        2. Configuration file value
        3. Default value (lowest priority)

        A key that is present in the configuration file but explicitly set to null is
        treated the same as a missing key: the value falls through to the default
        instead of resolving to None. Combined with ``update``, this is what lets a
        property such as the encryption key be cleared by writing null to the file.

        Includes intelligent type conversion for boolean and integer values, and
        list parsing from environment variables using common separators. The type
        to convert to is taken from the default value, since environment variables
        are always read as strings. Values that can't be converted fall back to the
        default instead of raising an error.

        Args:
            file_config (dict[str, Any]): Dictionary containing configuration file data.

        Returns:
            Any: The resolved configuration value with appropriate type conversion.
        """
        # Priority: environment variable > config file > default value
        value = self.default
        env_value = os.getenv(self.env) if self.env else None
        if env_value:
            value = env_value
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
            for key in self.file.split("."):
                if key not in value_from_file:
                    found = False
                    break
                value_from_file = value_from_file.get(key, {})
            if found and value_from_file is not None:
                value = value_from_file
        # Convert to bool if needed
        if isinstance(self.default, bool) and not isinstance(value, bool):
            value = str(value).lower() == "true"
        # Convert to int if needed
        elif isinstance(self.default, int) and not isinstance(value, int):
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = self.default
        return value

    def update(self, rekono_config: "RekonoConfig", value: Any) -> None:
        """Update configuration file with new property value.

        Updates the configuration file on disk with the new value while
        preserving the existing structure and other configuration values.
        Creates nested dictionaries as needed for dot-separated paths.

        Passing None as value writes an explicit null rather than removing the key.
        Since ``read`` treats a null file value the same as a missing one, this is how
        the encryption key is cleared: calling ``update`` with None makes the next
        ``read`` fall back to its default of None instead of returning the old key.

        Args:
            rekono_config (RekonoConfig): RekonoConfig instance for file access.
            value (Any): New value to store in the configuration file, or None to clear it.
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
    """Main configuration manager for Rekono platform.

    Provides centralized configuration management with support for multiple
    configuration sources, automatic directory initialization, and type-safe
    property access for all Rekono subsystems.

    The configuration system supports both production and testing modes with
    separate directory structures and automatic test environment isolation.
    All sensitive configuration values support multiple source options with
    intelligent precedence handling.

    Attributes:
        testing (bool): Flag indicating if running in test mode.
        base_dir (Path): Base directory path for the application.
        _home (Property): Home directory configuration property.
        _db_name (Property): Database name configuration property.
        _db_user (Property): Database username configuration property.
        _db_password (Property): Database password configuration property.
        _db_host (Property): Database host configuration property.
        _db_port (Property): Database port configuration property.
        _rq_host (Property): Redis Queue host configuration property.
        _rq_port (Property): Redis Queue port configuration property.
        _frontend_url (Property): Frontend URL configuration property.
        _frontend_desktop (Property): Frontend Desktop configuration property.
        _trusted_proxies (Property): Trusted proxies configuration property.
        _allowed_hosts (Property): Allowed hosts list configuration property.
        _encryption_key (Property): Encryption key configuration property.
        _secret_key (Property): Django secret key configuration property.
        _secure_cookies (Property): Secure cookies configuration property.
        _otp_expiration_hours (Property): OTP expiration time configuration property.
        _mfa_expiration_minutes (Property): MFA expiration time configuration property.
        _pdf_report_template (Property): PDF report template path property.
        _cmseek_dir (Property): CMSeek tool directory configuration property.
        _log4j_scan_dir (Property): Log4j scanner directory configuration property.
        _spring4shell_scan_dir (Property): Spring4Shell scanner directory configuration property.
        _emailharvester_dir (Property): EmailHarvester tool directory configuration property.
        _gittools_dir (Property): GitTools directory configuration property.

    Example:
        Access database configuration:

        ```python
        config = RekonoConfig()
        db_host = config.db_host
        db_port = config.db_port
        ```
    """

    testing = "test" in sys.argv
    # Directories
    base_dir = Path(__file__).resolve().parent.parent
    _home = Property("REKONO_HOME", default="/opt/rekono")
    # Database
    _db_name = Property("RKN_DB_NAME", "database.name", "rekono")
    _db_user = Property("RKN_DB_USER", "database.user", "")
    _db_password = Property("RKN_DB_PASSWORD", "database.password", "")
    _db_host = Property("RKN_DB_HOST", "database.host", "127.0.0.1")
    _db_port = Property("RKN_DB_PORT", "database.port", 5432)
    # RQ
    _rq_host = Property("RKN_RQ_HOST", "rq.host", "127.0.0.1")
    _rq_port = Property("RKN_RQ_PORT", "rq.port", 6379)
    # Frontend
    _frontend_url = Property("RKN_FRONTEND_URL", "frontend.url", "https://127.0.0.1")
    _frontend_desktop = Property("RKN_FRONTEND_DESKTOP", "frontend.desktop", False)
    # Infrastructure context
    _trusted_proxies = Property("RKN_TRUSTED_PROXIES", None, 0)
    # Security
    _allowed_hosts = Property("RKN_ALLOWED_HOSTS", "security.allowed-hosts", ["localhost", "127.0.0.1", "::1"])
    _encryption_key = Property(None, "security.encryption-key", None)
    _secret_key = Property("RKN_SECRET_KEY", "security.secret-key", Crypto.random(3000))
    _secure_cookies = Property("RKN_COOKIES_SECURE", "security.cookies.secure", False)
    _otp_expiration_hours = Property(None, None, 24)
    _mfa_expiration_minutes = Property(None, None, 15)
    # Templates
    _pdf_report_template = Property(None, "reports.pdf-template", None)
    # Tools
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
        """Get production home directory path.

        Returns:
            Path: Path to the production home directory, falling back to
            parent directory structure if configured path doesn't exist.
        """
        # Fallback to the parent of the backend directory
        home_value = Path(self._home.read())
        return home_value if home_value.is_dir() else self.base_dir.parent

    @property
    def home(self) -> Path:
        """Get current home directory path.

        Returns:
            Path: Path to the appropriate home directory (test or production).
        """
        return self._initialize_directory(self.base_dir / "tests" / "home" if self.testing else self.pro_home)

    @cached_property
    def pro_config_file(self) -> Path:
        """Get production configuration file path.

        Searches for the first existing configuration file using standard
        naming conventions in the home directory.

        Returns:
            Path: Path to the first found configuration file.
        """
        for filename in ["config.yaml", "config.yml", "rekono.yaml", "rekono.yml"]:
            path = self.pro_home / filename
            if path.is_file():
                break
        return path

    @cached_property
    def config_file(self) -> Path:
        """Get current configuration file path.

        Returns:
            Path: Path to the appropriate configuration file (test or production).
        """
        # In test mode, copy the config file to the test home directory
        if self.testing:
            shutil.copy(self.pro_config_file, self.home)
            return self.home / self.pro_config_file.name
        return self.pro_config_file

    @property
    def config_from_file(self) -> dict[str, Any]:
        """Load configuration data from YAML file.

        Not cached: the file is re-read and re-parsed on every access, so a value
        written by ``Property.update`` is visible to the very next ``Property.read``
        without needing to restart the process.

        Returns:
            dict[str, Any]: Dictionary containing all configuration data from the YAML file.
        """
        with self.config_file.open("r") as file:
            return yaml.safe_load(file)

    @property
    def reports(self) -> Path:
        """Get reports directory path.

        Returns:
            Path: Path to the reports directory, creating it if necessary.
        """
        return self._initialize_directory(self.home / "reports")

    @property
    def generated_reports(self) -> Path:
        """Get generated reports directory path.

        Returns:
            Path: Path to the generated reports subdirectory, creating it if necessary.
        """
        return self._initialize_directory(self.reports / "generated")

    @property
    def wordlists(self) -> Path:
        """Get wordlists directory path.

        Returns:
            Path: Path to the wordlists directory, creating it if necessary.
        """
        return self._initialize_directory(self.home / "wordlists")

    @property
    def logs(self) -> Path:
        """Get logs directory path.

        Returns:
            Path: Path to the logs directory, creating it if necessary.
        """
        return self._initialize_directory(self.home / "logs")

    @property
    def encryption_key(self) -> str | None:
        """Get encryption key for sensitive data protection.

        A random key is generated on every access in testing mode, rather than read
        from the configuration file, so tests never depend on a real encryption key
        being configured.

        Returns:
            str | None: Encryption key string, or None if not configured and not testing.
        """
        return Crypto.generate_encryption_key() if self.testing else self._encryption_key.read(self.config_from_file)

    @property
    def pdf_report_template(self) -> Path | None:
        """Get PDF report template file path.

        Searches for PDF report template in configured location or
        default locations within the application structure.

        Returns:
            Path | None: Path to the PDF report template file, or None if not found.
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
        """Get frontend application URL.

        The URL may include a path component when the frontend is exposed under
        a root path by a reverse proxy (e.g. ``https://localhost/rekono``). Any
        trailing slash is removed so links can be built as ``{frontend_url}/...``.

        Returns:
            str: Base URL for the Rekono frontend application.
        """
        return str(self._frontend_url.read(self.config_from_file)).rstrip("/")

    @property
    def frontend_origin(self) -> str:
        """Get the frontend origin (scheme and host) without any path.

        Used for CORS headers, which must reference an origin rather than a full
        URL with a path component.

        Returns:
            str: Origin of the frontend application (e.g. ``https://localhost``).
        """
        parsed = urlparse(self.frontend_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    @property
    def frontend_desktop(self) -> bool:
        """Get whether desktop app (Electron) support is enabled.

        When enabled, relaxes cookie SameSite policy to Lax and adds
        CORS headers allowing requests from the Electron app:// origin.

        Returns:
            bool: True if desktop app support is enabled.
        """
        return self._frontend_desktop.read(self.config_from_file)

    @property
    def root_path(self) -> str:
        """Get application root path.

        The root path is derived from the path component of the frontend URL,
        since the frontend and backend are expected to be exposed under the same
        prefix by a reverse proxy. A frontend URL without a path (or with just
        ``/``) means no root path. The result is normalized with a leading slash
        and without a trailing slash.

        Returns:
            str: Root path prefix for the application, or an empty string.
        """
        path = urlparse(self.frontend_url).path.strip("/")
        return f"/{path}" if path else ""

    @property
    def secret_key(self) -> str:
        """Get Django secret key.

        Returns:
            str: Secret key for Django cryptographic operations.
        """
        return self._secret_key.read(self.config_from_file)

    @property
    def secure_cookies(self) -> bool:
        """Get whether auth cookies should be sent over HTTPS only.

        Returns:
            bool: True if the ``Secure`` cookie flag should be set.
        """
        return self._secure_cookies.read(self.config_from_file)

    @property
    def allowed_hosts(self) -> list[str]:
        """Get allowed host names for Django.

        Returns:
            list[str]: List of allowed host names for HTTP requests.
        """
        return self._allowed_hosts.read(self.config_from_file)

    @property
    def trusted_proxies(self) -> int:
        """Get trusted proxy configuration.

        Returns:
            int: Number of trusted proxies in front of Rekono, or 0 if there is none.
        """
        return self._trusted_proxies.read(self.config_from_file)

    @property
    def otp_expiration_hours(self) -> int:
        """Get OTP expiration time in hours.

        Returns:
            int: Number of hours before OTP tokens expire.
        """
        return self._otp_expiration_hours.read(self.config_from_file)

    @property
    def mfa_expiration_minutes(self) -> int:
        """Get MFA expiration time in minutes.

        Returns:
            int: Number of minutes before MFA tokens expire.
        """
        return self._mfa_expiration_minutes.read(self.config_from_file)

    @property
    def db_name(self) -> str:
        """Get database name.

        Returns:
            str: PostgreSQL database name.
        """
        return self._db_name.read(self.config_from_file)

    @property
    def db_user(self) -> str:
        """Get database username.

        Returns:
            str: PostgreSQL database username.
        """
        return self._db_user.read(self.config_from_file)

    @property
    def db_password(self) -> str:
        """Get database password.

        Returns:
            str: PostgreSQL database password.
        """
        return self._db_password.read(self.config_from_file)

    @property
    def db_host(self) -> str:
        """Get database host.

        Returns:
            str: PostgreSQL database host address.
        """
        return self._db_host.read(self.config_from_file)

    @property
    def db_port(self) -> int:
        """Get database port.

        Returns:
            int: PostgreSQL database port number.
        """
        return self._db_port.read(self.config_from_file)

    @property
    def rq_host(self) -> str:
        """Get Redis Queue host.

        Returns:
            str: Redis host address for background job processing.
        """
        return self._rq_host.read(self.config_from_file)

    @property
    def rq_port(self) -> int:
        """Get Redis Queue port.

        Returns:
            int: Redis port number for background job processing.
        """
        return self._rq_port.read(self.config_from_file)

    @property
    def cmseek_dir(self) -> str:
        """Get CMSeek tool directory.

        Returns:
            str: Path to CMSeek tool installation directory.
        """
        return self._cmseek_dir.read(self.config_from_file)

    @property
    def log4j_scan_dir(self) -> str:
        """Get Log4j scanner directory.

        Returns:
            str: Path to Log4j vulnerability scanner installation directory.
        """
        return self._log4j_scan_dir.read(self.config_from_file)

    @property
    def spring4shell_scan_dir(self) -> str:
        """Get Spring4Shell scanner directory.

        Returns:
            str: Path to Spring4Shell vulnerability scanner installation directory.
        """
        return self._spring4shell_scan_dir.read(self.config_from_file)

    @property
    def emailharvester_dir(self) -> str:
        """Get EmailHarvester tool directory.

        Returns:
            str: Path to EmailHarvester tool installation directory.
        """
        return self._emailharvester_dir.read(self.config_from_file)

    @property
    def gittools_dir(self) -> str:
        """Get GitTools directory.

        Returns:
            str: Path to GitTools installation directory.
        """
        return self._gittools_dir.read(self.config_from_file)

    def _initialize_directory(self, path: Path) -> Path:
        """Initialize directory by creating it if it doesn't exist.

        Args:
            path (Path): Path to the directory to initialize.

        Returns:
            Path: The initialized directory path.
        """
        path.mkdir(exist_ok=True)
        return path
