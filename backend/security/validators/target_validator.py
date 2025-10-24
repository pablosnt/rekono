"""Target validation utilities for security testing workflows.

Provides specialized validation for penetration testing targets including
IP addresses, networks, domains, and URLs. This module implements security
controls to prevent testing of unauthorized or restricted targets through
configurable deny lists and policy enforcement.
"""

import ipaddress
import re
from re import RegexFlag
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from framework.logging import LoggingEntity
from security.validators.enums import Regex
from target_denylist.models import TargetDenylist


class TargetValidator(RegexValidator, LoggingEntity):
    """Validator for penetration testing targets with deny list enforcement.

    Validates security testing targets against both regex patterns and
    configurable deny lists to prevent unauthorized testing. Supports
    validation of IP addresses, networks, domains, and regex patterns.

    Security Features:
        - Deny list enforcement for restricted targets
        - Regex pattern matching for flexible target specification
        - IPv4/IPv6 network range validation and blocking
        - Policy-based target restriction enforcement
        - Comprehensive validation error reporting

    Validation Process:
        1. Basic regex pattern validation
        2. Exact target deny list matching
        3. Regex pattern deny list matching
        4. IP network range deny list validation
        5. Comprehensive error handling and reporting

    Args:
        regex (Any): Regex pattern for target format validation.
        message (Any | None): Custom validation error message.
        code (str | None): Error code for validation failures (default: 'target').
        inverse_match (bool | None): Whether to invert regex matching (default: False).
        flags (RegexFlag | None): Regex compilation flags.

    Attributes:
        code (str | None): Error code used for validation failure exceptions.
    """

    def __init__(
        self,
        regex: Regex | str,
        message: Any | None = "Target is disallowed by policy",
        code: str | None = "target",
        inverse_match: bool | None = False,
        flags: RegexFlag | None = None,
    ) -> None:
        """Initialize the target validator with configuration parameters.

        Sets up the validator with regex pattern, error handling, and deny list
        enforcement configuration. Configures the underlying RegexValidator with
        the provided parameters while storing the error code for validation failures.

        Args:
            regex (Regex | str): Regex pattern enum for target format validation.
            message (Any | None): Custom error message for validation failures.
            code (str | None): Error code for ValidationError exceptions (default: 'target').
            inverse_match (bool | None): Whether to invert the regex matching logic (default: False).
            flags (RegexFlag | None): Regex compilation flags for pattern matching.
        """
        self.code = code
        # isinstance verification is needed to keep compatibility with old database migrations
        super().__init__(regex.value if isinstance(regex, Regex) else regex, message, code, inverse_match, flags)

    def __call__(self, value: str | None) -> None:
        """Validate target against regex patterns and deny lists.

        Performs comprehensive target validation including regex pattern matching,
        exact deny list checking, regex pattern deny list matching, and IP network
        range validation to ensure only authorized targets are tested.

        Args:
            value (str | None): The target to validate (IP, domain, URL, etc.).

        Raises:
            ValidationError: If target is invalid, missing, or denied by policy.
        """
        super().__call__(value)
        if not value:
            raise ValidationError("Target is required", code=self.code, params={"value": value})
        denylist = TargetDenylist.objects.all().values_list("target", flat=True)
        if value in denylist:
            self.logger.warning(f"[Security] Target '{value}' is denied by policy")
            raise ValidationError(self.message, code=self.code, params={"value": value})
        for denied_value in denylist:
            try:
                match = re.fullmatch(denied_value, value)
            except Exception:
                match = None
            if bool(match):
                self.logger.warning(f"[Security] Target '{value}' match the denied value {denied_value}")
                raise ValidationError(self.message, code=self.code, params={"value": value})
            for address_class, network_class in [
                (ipaddress.IPv4Address, ipaddress.IPv4Network),
                (ipaddress.IPv6Address, ipaddress.IPv6Network),
            ]:
                try:
                    if address_class(value) in network_class(denied_value):
                        self.logger.warning(f"[Security] Target '{value}' belongs to the denied network {denied_value}")
                        raise ValidationError(self.message, code=self.code, params={"value": value})
                except ipaddress.AddressValueError:
                    pass
