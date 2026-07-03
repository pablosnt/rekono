"""Django models for Rekono's core framework infrastructure.

Provides base model classes with security features, encryption support, and
common functionality used across all Rekono modules. Includes project-level
access control, input parsing capabilities, and secure field handling.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, cast

import requests
import urllib3
from django.db.models import ManyToManyField, Model, Q, TextChoices

from framework.cache import Cache
from framework.enums import InputKeyword
from framework.logging import LoggingEntity
from rekono.settings import AUTH_USER_MODEL, CONFIG
from security.cryptography import Crypto


class BaseModel(Model, LoggingEntity):
    """Abstract base model providing common functionality for all Rekono models.

    Extends Django's Model class with logging capabilities and project-level access
    control. All models in Rekono inherit from this base class to ensure consistent
    behavior and security enforcement across the platform.

    Security Features:
        - Project-level access control through _project_field configuration
        - Integration with logging infrastructure for audit trails
        - Standardized string representation for debugging and logging

    Attributes:
        _project_field (str): Field path to the associated project for access control.
                             Empty string indicates no project association.

    Example:
        Create a model with project association:

        ```python
        class MyModel(BaseModel):
            _project_field = "target__project"
            name = models.CharField(max_length=100)
        ```
    """

    _project_field = ""

    class Meta:
        """Django Meta class configuration for BaseModel.

        Configures BaseModel as an abstract base class that provides common
        functionality without creating its own database table.

        Attributes:
            abstract (bool): Marks this model as abstract (no database table).
        """

        abstract = True

    @cached_property
    def parent_project(self) -> Any | list[Any] | None:
        """Get the project associated with this model instance.

        Traverses the field path specified in _project_field to locate the
        associated project object. This enables project-level access control
        and permission enforcement.

        Returns:
            Any | list[Any] | None: The associated project object, list of projects,
                                   or None if no project association exists.
        """
        filter_field = self.__class__._project_field
        if filter_field:
            project = self
            for field in filter_field.split("__"):
                if hasattr(project, field) and getattr(project, field):
                    project = getattr(project, field)
                else:
                    return None
            return project

    def __str__(self) -> str:
        """Return string representation of the model instance.

        Returns:
            str: The class name of the model instance.
        """
        return self.__class__.__name__


class BaseEncrypted(BaseModel):
    """Abstract base model providing encryption capabilities for sensitive data.

    Extends BaseModel with automatic encryption and decryption of sensitive fields.
    Uses AES encryption when encryption keys are configured, providing transparent
    data protection for sensitive information like passwords and tokens.

    Security Features:
        - Automatic AES encryption for sensitive data fields
        - Transparent encryption/decryption through property accessors
        - Secure key management integration
        - Fallback to plain text when encryption is not configured

    Attributes:
        _encryptor (Crypto | None): The encryption instance for secure operations.
        _encrypted_field (str): Name of the database field storing encrypted data.

    Example:
        Create a model with encrypted secret field:

        ```python
        class SecretModel(BaseEncrypted):
            _secret = models.TextField(db_column="secret")
            _encrypted_field = "_secret"

        # Usage
        model = SecretModel()
        model.secret = "sensitive_data"  # Automatically encrypted
        plain_text = model.secret  # Automatically decrypted
        ```
    """

    class Meta:
        """Django Meta class configuration for BaseEncrypted.

        Configures BaseEncrypted as an abstract base class that extends
        BaseModel with encryption capabilities without creating its own table.

        Attributes:
            abstract (bool): Marks this model as abstract (no database table).
        """

        abstract = True

    _encryptor = Crypto(CONFIG.encryption_key) if CONFIG.encryption_key else None
    _encrypted_field = "_secret"

    @property
    def secret(self) -> str | None:
        """Get the decrypted value of the encrypted field.

        Automatically decrypts the stored encrypted value using the configured
        encryptor. Returns None if the field is empty or encryption is not configured.

        Returns:
            str | None: The decrypted secret value or None if empty.
        """
        return (
            (
                self._encryptor.decrypt(getattr(self, self._encrypted_field))
                if self._encryptor
                else getattr(self, self._encrypted_field)
            )
            if hasattr(self, self._encrypted_field) and getattr(self, self._encrypted_field)
            else None
        )

    @secret.setter
    def secret(self, value: str) -> None:
        """Set the encrypted field with automatic encryption.

        Automatically encrypts the provided value using the configured encryptor
        before storing it in the database field. Falls back to plain text storage
        when encryption is not configured.

        Args:
            value (str): The plain text value to encrypt and store.
        """
        if hasattr(self, self._encrypted_field):
            setattr(
                self,
                self._encrypted_field,
                (self._encryptor.encrypt(value) if self._encryptor and value is not None else value),
            )


class BaseInput(BaseModel):
    """Abstract base model for input data used in security tool execution.

    Provides parsing and filtering capabilities for various input types used by
    security tools. Supports complex filtering logic, URL generation and validation, and data
    transformation for tool integration.

    Attributes:
        _filters (list[Filter]): List of Filter instances for input validation.
        _parse_mapping (dict): Mapping of InputKeyword to field names or functions.
        _parse_dependencies (list[str]): List of dependent fields to parse first.
        _url_cache (Cache): Shared cache of probed URL reachability results, used by
                          get_url to avoid repeating the same HTTP request.

    Example:
        Create an input model with filtering:

        ```python
        class PortInput(BaseInput):
            port = models.IntegerField()
            service = models.CharField(max_length=50)

            _filters = [
                BaseInput.Filter(type=str, field="service", contains=True)
            ]
            _parse_mapping = {
                InputKeyword.PORT: "port",
                InputKeyword.TARGET: lambda instance, target: f"{instance.host}:{instance.port}"
            }
        ```
    """

    class Meta:
        """Django Meta class configuration for BaseInput.

        Configures BaseInput as an abstract base class for input data models
        used in security tool execution without creating its own table.

        Attributes:
            abstract (bool): Marks this model as abstract (no database table).
        """

        abstract = True

    _url_cache = Cache(prefix="url")

    @dataclass
    class Filter:
        """Filter configuration for input validation and processing.

        Defines how input values should be filtered and validated based on
        tool argument requirements. Supports type checking, string matching,
        and custom processing functions.

        Attributes:
            type (type): The expected data type for validation.
            field (str): The model field name to validate against.
            contains (bool): Whether to use substring matching instead of exact matching.
            processor (Callable[[Any], Any] | None): Optional preprocessing function.
        """

        type: type
        field: str
        contains: bool = False
        processor: Callable[[Any], Any] | None = None

        def filter(self, expected: str, value: Any, is_negative: bool = False) -> bool:
            """Apply the filter to validate an input value.

            Performs validation based on the filter configuration, supporting
            type conversion, negation, and custom processing.

            Args:
                expected (str): The expected value to match against.
                value (Any): The actual value to validate.
                is_negative (bool): Whether to negate the filter result.

            Returns:
                bool: True if the value passes the filter, False otherwise.
            """
            # If a processor is defined, preprocess the value before filtering
            if self.processor:
                value = self.processor(value)
            try:
                # If the filter type is a Django TextChoices enum, compare by name
                return (
                    issubclass(self.type, TextChoices)
                    and self._compare(expected.upper(), cast(TextChoices, self.type)(value).name, is_negative)
                ) or (
                    # For string or integer types, compare as lowercased strings
                    self.type in [str, int]
                    and self._compare(
                        str(expected).strip().lower(), str(value).strip().lower(), is_negative, self.contains
                    )
                )
            except (ValueError, KeyError):  # pragma: no cover
                # If conversion fails, the filter does not match
                return False

        def _compare(self, expected: str, value: str, negative: bool = False, contains: bool = False) -> bool:
            """Compare expected and actual values with optional negation.

            Args:
                expected (str): The expected value.
                value (str): The actual value.
                negative (bool): Whether to negate the comparison result.
                contains (bool): Whether to use substring matching.

            Returns:
                bool: The comparison result, optionally negated.
            """
            conclusion = expected == value if not contains else expected in value
            return conclusion if not negative else not conclusion

    _filters: list[Filter] = []
    _parse_mapping: dict[InputKeyword, str | Callable | dict[str, str]] = {}
    _parse_dependencies: list[str] = []

    @cached_property
    def input_type(self) -> Any:
        """Get the InputType associated with this model.

        Looks up the InputType based on the model's app label and model name,
        supporting both primary and fallback model references.

        Returns:
            Any: The associated InputType instance or None if not found.
        """
        from input_types.models import InputType

        reference = f"{self._meta.app_label}.{self._meta.model_name}"
        return InputType.objects.filter(Q(model=reference) | Q(fallback_model=reference)).first()

    def clean_path(self, value: str | None) -> str | None:
        """Normalize a path string by ensuring it starts with a forward slash.

        Args:
            value (str | None): The path string to normalize.

        Returns:
            str | None: The normalized path with leading slash or None if empty.
        """
        return f"/{value}" if value and len(value) > 1 and value[0] != "/" else value

    def get_url(
        self,
        target: Any,
        host: str,
        port: int | None = None,
        endpoint: str | None = None,
        protocols: list[str] = ["http", "https"],
    ) -> str | None:
        """Construct and validate a URL with automatic protocol detection.

        Attempts to construct a valid URL by testing different protocols and
        validating connectivity. Enhanced with target context to use target
        ports when no specific port is provided. Each protocol/port
        combination's reachability is looked up in _url_cache before issuing
        a request, and the result is cached afterwards, so repeated calls
        for the same URL (e.g. across multiple tool arguments) don't repeat
        the same HTTP request.

        Args:
            target (Any): Target context containing port information
            host (str): The hostname or IP address.
            port (int | None): The port number (optional).
            endpoint (str | None): The endpoint path (optional).
            protocols (list[str]): List of protocols to test (default: ["http", "https"]).

        Returns:
            str | None: A valid URL string or None if no working URL found.
        """
        # Disable SSL warnings since we're testing connectivity with disabled certificate verification
        urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

        # Normalize endpoint parameter: ensure it doesn't start with '/' to avoid double slashes in URL
        if endpoint is None:
            endpoint = ""
        elif endpoint.startswith("/"):
            # Remove leading slash since we'll add it in the schema template
            endpoint = endpoint[1:]
        # Define URL schema template with placeholders for dynamic components
        schema = "{protocol}://{host}:{port}/{endpoint}"
        # Determine which ports to test based on input parameters
        ports = (
            [port]
            if port
            # If no port specified, try to use target ports, otherwise default to common web ports
            else ([tp.port for tp in target.target_ports.all()] if target.target_ports.exists() else [80, 443])
        )
        # Test all combinations of ports and protocols to find a working URL
        for port in ports:
            for protocol in protocols:
                # Skip invalid protocol/port combinations to avoid unnecessary requests
                # Don't try HTTPS on port 80 or HTTP on port 443 when both protocols are available
                if len(protocols) > 1 and (port == 80 and protocol == "https") or (port == 443 and protocol == "http"):
                    continue
                # Construct the URL using the current protocol/port combination
                url_to_test = schema.format(protocol=protocol, host=host, port=port, endpoint=endpoint)
                # Reuse a previous probe of this exact URL instead of issuing another request
                cached_result = self._url_cache.get(url_to_test)
                if cached_result is not None:
                    if cached_result == "1":
                        return url_to_test
                    continue
                try:
                    # Attempt to connect to the URL to verify it's accessible
                    # Use disabled SSL verification for testing purposes and short timeout for efficiency
                    # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
                    requests.get(url_to_test, timeout=5, verify=False)
                    # If the request succeeds, return this working URL
                    self._url_cache.set(url_to_test, "1")
                    return url_to_test
                except Exception:
                    # If connection fails, try the next protocol/port combination
                    self._url_cache.set(url_to_test, "0")
                    continue

    def filter(self, argument_input: Any, target: Any = None) -> bool:
        """Apply complex filtering logic based on tool argument requirements.

        Processes filter strings with AND/OR logic and negation support.
        Supports complex conditions like "condition1 and condition2" or
        "condition1 or condition2", and negative conditions prefixed with "!".

        Args:
            argument_input (Any): The tool argument input with filter configuration.
            target (Any): Optional target context for filtering (used in subclasses implementation).

        Returns:
            bool: True if the input passes all filter conditions, False otherwise.
        """
        if not argument_input.filter:
            return True
        # Determine the logical operator (AND/OR) and set processing mode
        # This allows for complex conditions like "condition1 and condition2 or condition3"
        if " or " in argument_input.filter:
            operator = " or "
            is_or = True
        else:
            operator = " and "
            is_or = False
        # Track overall conclusion - starts as True for AND operations
        conclusion = True
        # Process each condition in the filter string
        for condition in argument_input.filter.split(operator):
            # Handle negative conditions (prefixed with "!")
            # Example: "!admin" means "not admin"
            is_negative = condition.startswith("!")
            if is_negative:
                condition = condition[1:]  # Remove the "!" prefix
            # Track if any filter matches this condition
            filter_conclusion = False
            # Try each configured filter against this condition
            for filter in self._filters:
                # Each filter is responsible for checking if the condition matches
                _conclusion = filter.filter(condition, getattr(self, filter.field), is_negative)
                if _conclusion:
                    # For OR operations: return immediately on first match
                    # For AND operations: continue checking other filters
                    if is_or:
                        return True
                    else:
                        filter_conclusion = True
                        break  # Found a match for this condition, move to next
            # For AND operations: all conditions must be true
            # For OR operations: at least one condition must be true (handled above)
            conclusion = conclusion and filter_conclusion
        return conclusion

    def parse(self, target: Any, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Parse input data into a format suitable for tool execution.

        Processes the input data according to the configured parse mapping,
        handling dependencies and accumulation strategies. Enhanced with target
        context for improved URL generation.

        Args:
            target (Any): Target context for parsing (e.g., for URL generation)
            accumulated (dict[str, Any]): Previously accumulated parsing data.

        Returns:
            dict[str, Any]: Parsed data ready for tool execution.

        Note:
            Dependencies are parsed first to ensure required data is available
            when processing the main parsing mappings.
        """
        result = {}
        # Process dependencies first - these must be parsed before current input
        # This ensures that related inputs are available when processing mappings
        for dependency in self._parse_dependencies:
            if (
                hasattr(self, dependency)
                and getattr(self, dependency)
                and isinstance(getattr(self, dependency), BaseInput)
            ):
                # Recursively parse dependent inputs and merge results
                result.update(getattr(self, dependency).parse(accumulated))
        # Process the main parsing mappings
        for keyword, field_or_function in self._parse_mapping.items():
            # Extract value based on mapping type:
            # - String: direct field access
            # - Callable: function call with self as parameter
            # - Any: direct value assignment
            value = (
                getattr(self, field_or_function)
                if isinstance(field_or_function, str) and hasattr(self, field_or_function)
                else (field_or_function(self, target) if callable(field_or_function) else field_or_function)
            )
            if value is None:
                continue
            key = keyword.name.lower()
            current_value = accumulated.get(key)
            # Handle accumulation logic for different data types
            if current_value is not None:
                # For lists: append new values to existing list
                if isinstance(current_value, list):
                    result[key] = accumulated.get(key, []) + (value if isinstance(value, list) else [value])
                    continue
                # For dicts: merge dictionaries
                elif isinstance(current_value, dict) and isinstance(value, dict):
                    result[key] = {**accumulated.get(key, {}), **value}
                    continue
            # Default case: assign value directly
            result[key] = value
        return result

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        """Create a finding from user input parameters.

        Override this method in subclasses to create specific finding types
        from user input parameters. Used for establishing relationships between
        user-provided data and tool execution findings.

        Args:
            execution (Any): The execution context for the finding
            **fields (Any): Additional fields for the finding

        Returns:
            Any | None: Created finding instance or None if not applicable
        """
        return None  # pragma: no cover


class BaseLike(BaseModel):
    """Abstract base model providing like/favorite functionality.

    Enables users to like or favorite model instances through a many-to-many
    relationship. Commonly used for findings, notes, and other user-interactive
    content to track user preferences and engagement.

    Attributes:
        liked_by (ManyToManyField): Users who have liked this instance.

    Example:
        Create a likeable model:

        ```python
        class LikeableContent(BaseLike):
            title = models.CharField(max_length=200)
            content = models.TextField()

        # Usage
        content = LikeableContent.objects.get(id=1)
        content.liked_by.add(user)  # User likes the content
        is_liked = content.liked_by.filter(id=user.id).exists()
        ```
    """

    liked_by = ManyToManyField(AUTH_USER_MODEL, related_name="liked_%(class)s")

    class Meta:
        """Django Meta class configuration for BaseLike.

        Configures BaseLike as an abstract base class that provides like/favorite
        functionality without creating its own database table.

        Attributes:
            abstract (bool): Marks this model as abstract (no database table).
        """

        abstract = True
