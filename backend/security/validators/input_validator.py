"""Input validation utilities with regex patterns and security controls.

Provides comprehensive input validation including regex patterns, injection
prevention, and custom validators for secure data processing. This module
implements defense-in-depth validation to prevent common security vulnerabilities
including injection attacks and malformed input exploitation.
"""

import re
from re import RegexFlag
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

from framework.logging import LoggingEntity
from security.validators.enums import Regex


class Validator(RegexValidator, LoggingEntity):
    """Enhanced regex validator with injection prevention and security logging.

    Extends Django's RegexValidator with additional security features including
    injection attack detection, comprehensive logging, and customizable validation
    rules. This validator provides defense-in-depth input validation.

    Security Features:
        - Regex pattern validation with full match requirements
        - Injection attack detection and prevention
        - Security event logging for validation failures
        - Configurable validation rules per field type
        - Required value enforcement

    Args:
        regex (Regex): The regex pattern to use for validation.
        message (Any | None): Custom validation error message.
        code (str | None): Error code for validation failures.
        inverse_match (bool | None): Whether to invert the match logic.
        flags (RegexFlag | None): Regex compilation flags.
        deny_injections (bool): Enable injection attack detection (default: False).
    """

    def __init__(
        self,
        regex: Regex | str,
        message: Any | None = "Provided value contains disallowed characters",
        code: str | None = None,
        inverse_match: bool | None = ...,  # type: ignore
        flags: RegexFlag | None = None,
        deny_injections: bool = False,
    ) -> None:
        """Initialize the enhanced validator with security configuration.

        Sets up the validator with regex pattern matching, injection detection,
        and comprehensive validation rules. Configures the underlying RegexValidator
        with the provided parameters while adding security-specific features.

        Args:
            regex (Regex | str): The regex pattern enum to use for validation.
            message (Any | None): Custom error message for validation failures.
            code (str | None): Error code for ValidationError exceptions.
            inverse_match (bool | None): Whether to invert the regex matching logic.
            flags (RegexFlag | None): Regex compilation flags for pattern matching.
            deny_injections (bool): Enable injection attack detection (default: False).
        """
        self.deny_injections = deny_injections
        # isinstance verification is needed to keep compatibility with old database migrations
        super().__init__(regex.value if isinstance(regex, Regex) else regex, message, code, inverse_match, flags)

    def __call__(self, value: str | None) -> None:
        """Validate input value against regex pattern and injection rules.

        Performs comprehensive validation including required value checking,
        regex pattern matching, and optional injection attack detection.
        Logs security events for all validation failures.

        Args:
            value (str | None): The input value to validate.

        Raises:
            ValidationError: If validation fails for any reason.
        """
        if not value:
            raise ValidationError("Value is required", code=self.code, params={"value": value})
        regex_matches = re.fullmatch(self.regex, value)
        if (
            (self.inverse_match and not bool(regex_matches))
            or (not self.inverse_match and bool(regex_matches))
            or (self.deny_injections and bool(re.findall(Regex.INJECTION.value, value)))
        ):
            self.logger.warning(f"[Security] Value '{value}' doesn't match the allowed regex")
            raise ValidationError(self.message, code=self.code, params={"value": value})


class FutureDatetimeValidator(RegexValidator):
    """Validator ensuring datetime values are in the future.

    Used for validating expiration dates, scheduled tasks, and other
    temporal fields that must be set to future dates for security
    and operational correctness.
    """

    def __call__(self, value: Any) -> None:
        """Validate that the datetime value is in the future.

        Args:
            value (Any): The datetime value to validate.

        Raises:
            ValidationError: If the datetime is not in the future.
        """
        if value <= timezone.now():
            raise ValidationError("Datetime must be future", code=self.code)


class PasswordValidator:
    """Comprehensive password validation with security requirements.

    Implements enterprise-grade password validation enforcing complexity
    requirements to ensure strong password security. This validator checks
    for minimum length, character diversity, and composition requirements.

    Security Requirements:
        - Minimum 12 characters length
        - At least one lowercase letter (a-z)
        - At least one uppercase letter (A-Z)
        - At least one digit (0-9)
        - At least one special character/symbol

    Attributes:
        full_match (str): Regex for overall password validation
        lowercase (str): Regex for lowercase character requirement
        uppercase (str): Regex for uppercase character requirement
        digit (str): Regex for digit character requirement
        symbol (str): Regex for symbol character requirement
    """

    full_match = r"[A-Za-z0-9\W]{12,}"  # Full match with all requirements
    lowercase = r"[a-z]"  # At least one lowercase
    uppercase = r"[A-Z]"  # At least one uppercase
    digit = r"[0-9]"  # At least one digit
    symbol = r"[\W]"  # At least one symbol

    def validate(self, password: str, user: Any = None) -> None:
        """Validate password against security requirements.

        Performs comprehensive password validation including length,
        character diversity, and composition requirements. Compatible
        with Django's password validation framework.

        Args:
            password (str): The password to validate.
            user (Any): The user object (for Django compatibility, unused).

        Raises:
            ValidationError: If password does not meet security requirements.
        """
        if not bool(re.fullmatch(self.full_match, password)):  # Full check
            raise ValidationError(self.get_help_text())
        for regex, char_type in [
            (self.lowercase, "lowercase"),
            (self.uppercase, "uppercase"),
            (self.digit, "digit"),
            (self.symbol, "symbol"),
        ]:
            if not bool(re.search(regex, password)):
                raise ValidationError(f"Your password must contain at least 1 {char_type}")

    def get_help_text(self) -> str:
        """Get password requirements help text.

        Returns:
            str: Human-readable description of password requirements.
        """
        return "Your password must contain at least 1 lowercase, 1 uppercase, 1 digit and 1 symbol"
