"""This module defines the core database models and ORM logic."""

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, cast

import requests
import urllib3
from django.db.models import ManyToManyField, Model, Q, TextChoices

from framework.enums import InputKeyword
from framework.logging import LoggingEntity
from rekono.settings import AUTH_USER_MODEL, CONFIG
from security.cryptography.encryption import Encryptor


class BaseModel(Model, LoggingEntity):
    """Base model class that provides common functionality for all models.

    This abstract base class extends Django's Model and LoggingEntity to provide
    project-based filtering and logging capabilities. It includes a mechanism
    to link models to projects through a configurable field path.

    Attributes:
        _project_field (str): Field path to the related project model.
                             Used for project-based filtering and authorization.
    """

    _project_field = ""

    class Meta:
        abstract = True

    @cached_property
    def parent_project(self) -> Any | list[Any] | None:
        """Get the parent project for this model instance.

        Traverses the project field path to find the associated project.
        If no project field is configured or the path is invalid, returns None.

        Returns:
            The parent project instance, list of projects, or None if not found.
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
        return None

    def __str__(self) -> str:
        """Return string representation of the model.

        Returns:
            The class name of the model.
        """
        return self.__class__.__name__


class BaseEncrypted(BaseModel):
    """Base model for encrypted data storage.

    This abstract base class provides encryption/decryption capabilities
    for sensitive data fields. It automatically handles encryption on save
    and decryption on retrieval.

    Attributes:
        _encryptor (Encryptor): Encryption utility instance.
        _encrypted_field (str): Name of the field containing encrypted data.
    """

    class Meta:
        abstract = True

    _encryptor = Encryptor(CONFIG.encryption_key) if CONFIG.encryption_key else None
    _encrypted_field = "_secret"

    @property
    def secret(self) -> str | None:
        """Get the decrypted secret value.

        Automatically decrypts the stored secret value when accessed.
        If no encryption key is configured, returns the raw value.

        Returns:
            The decrypted secret string or None if not set.
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
        """Set and encrypt the secret value.

        Automatically encrypts the value before storing it in the database.
        If no encryption key is configured, stores the raw value.

        Args:
            value: The secret string to encrypt and store.
        """
        if hasattr(self, self._encrypted_field):
            setattr(
                self,
                self._encrypted_field,
                (self._encryptor.encrypt(value) if self._encryptor and value is not None else value),
            )


class BaseInput(BaseModel):
    """Base model for input data processing and filtering.

    This abstract base class provides functionality for processing, filtering,
    and parsing data to be used as part of tool executions.

    Attributes:
        _filters (list[Filter]): List of filter configurations for this input type.
        _parse_mapping (dict): Mapping of input keywords to field names or functions.
        _parse_dependencies (list[str]): List of dependent fields that must be parsed first.
    """

    class Meta:
        abstract = True

    @dataclass
    class Filter:
        """Filter configuration for input data validation and processing.

        This inner class defines how input data should be filtered based on
        type, field, and custom processing logic.

        Attributes:
            type (type): The expected data type for this filter.
            field (str): The field name to filter on.
            contains (bool): Whether to use contains matching instead of exact matching.
            processor (Callable): Optional function to process the value before filtering.
        """

        type: type
        field: str
        contains: bool = False
        processor: Callable[[Any], Any] | None = None

        def filter(self, expected: str, value: Any, is_negative: bool = False) -> bool:
            """Apply the filter to a value.

            Args:
                expected: The expected value to compare.
                value: The value to filter against.
                is_negative: Whether this is a negative filter (NOT condition).

            Returns:
                True if the filter condition is met, False otherwise.
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
            except (ValueError, KeyError):
                # If conversion fails, the filter does not match
                return False

        def _compare(self, expected: str, value: str, negative: bool = False, contains: bool = False) -> bool:
            """Compare filter condition with value.

            Args:
                expected: The expected value to compare.
                value: The value to compare against.
                negative: Whether this is a negative comparison.
                contains: Whether to use contains matching.

            Returns:
                True if the comparison condition is met.
            """
            return (
                self._assert(expected, value, contains) if not negative else not self._assert(expected, value, contains)
            )

        def _assert(self, expected: str, value: str, contains: bool) -> bool:
            """Assert the comparison between filter and value.

            Args:
                expected: The expected value to compare.
                value: The value to compare against.
                contains: Whether to use contains matching.

            Returns:
                True if the assertion passes.
            """
            return expected == value if not contains else expected in value

    _filters: list[Filter] = []
    _parse_mapping: dict[InputKeyword, str | Callable | dict[str, str]] = {}
    _parse_dependencies: list[str] = []

    @cached_property
    def input_type(self) -> Any:
        """Get the input type configuration for this model.

        Returns:
            The InputType instance associated with this model.
        """
        from input_types.models import InputType

        reference = f"{self._meta.app_label}.{self._meta.model_name}"
        return InputType.objects.filter(Q(model=reference) | Q(fallback_model=reference)).first()

    def clean_path(self, value: str | None) -> str | None:
        """Clean and normalize a path string.

        Ensures the path starts with a forward slash if it's not empty
        and doesn't already start with one.

        Args:
            value: The path string to clean.

        Returns:
            The cleaned path string or None if input is None.
        """
        return f"/{value}" if value and len(value) > 1 and value[0] != "/" else value

    def get_url(
        self,
        host: str,
        port: int | None = None,
        endpoint: str | None = None,
        protocols: list[str] = ["http", "https"],
    ) -> str | None:
        """Generate and validate a URL for the given host and parameters.

        Attempts to connect to the host using different protocols and ports
        to find a working URL. Disables SSL warnings during testing.

        Args:
            host: The hostname or IP address.
            port: The port number (optional).
            endpoint: The endpoint path (optional).
            protocols: List of protocols to try (default: http, https).

        Returns:
            The first working URL found, or None if none work.
        """
        urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
        if endpoint is None:
            endpoint = ""
        elif endpoint.startswith("/"):
            endpoint = endpoint[1:]
        schema = "{protocol}://{host}/{endpoint}"
        if port:
            schema = "{protocol}://{host}:{port}/{endpoint}"  # Include port schema if port exists
            if port == 80:
                protocols = ["http"]
            elif port == 443:
                protocols = ["https"]
        for protocol in protocols:  # For each protocol
            url_to_test = schema.format(protocol=protocol, host=host, port=port, endpoint=endpoint)
            try:
                # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
                requests.get(url_to_test, timeout=5, verify=False)
                return url_to_test
            except Exception:
                continue
        return None

    def filter(self, argument_input: Any, target: Any = None) -> bool:
        """Filter this input based on argument input conditions.

        Applies complex filtering logic using AND/OR operators and
        the configured filters for this input type.

        Args:
            argument_input: The argument input containing filter conditions.
            target: Optional target object for additional filtering context.

        Returns:
            True if the input passes all filter conditions.
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

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Parse this input into a standardized format.

        Processes the input according to the configured mapping and dependencies,
        accumulating results with other parsed inputs.

        Args:
            accumulated: Dictionary of already parsed inputs to merge with.

        Returns:
            Dictionary containing the parsed input data.
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
                else (field_or_function(self) if isinstance(field_or_function, Callable) else field_or_function)
            )
            # Ensure we always have a string value (empty string if None)
            if value is None:
                value = ""
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


class BaseLike(BaseModel):
    """Base model for likeable entities.

    This abstract base class provides functionality for entities that can be
    liked by users. It includes a many-to-many relationship with users.

    Attributes:
        liked_by: Many-to-many field linking to users who liked this entity.
    """

    liked_by = ManyToManyField(AUTH_USER_MODEL, related_name="liked_%(class)s")

    class Meta:
        abstract = True
