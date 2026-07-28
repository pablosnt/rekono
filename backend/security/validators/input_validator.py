"""Validators used across Rekono's Django models to check field values.

Provides Validator, which checks a value against one of the shared Regex patterns
defined in security.validators.enums and can optionally reject values containing
injection characters or a sensitive environment-variable assignment. Also provides
FutureDatetimeValidator, for fields that must hold a future date, and
PasswordValidator, which enforces password complexity rules.
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
    """Regex validator with a required value check and optional injection detection.

    Extends Django's RegexValidator but overrides its call logic entirely: a
    missing or empty value is always rejected, the value must fully match (or,
    depending on inverse_match, must not match) the configured regex, and, when
    deny_injections is enabled, the value is also rejected if it contains a
    common injection character or a sensitive environment-variable assignment.

    Security Features:
        - Missing or empty values are always rejected
        - Full-string match against the configured regex, not a partial match
        - Optional rejection of injection characters (;"'&<>$) and sensitive
          environment-variable assignments (e.g. LD_PRELOAD=...) via deny_injections
        - Every rejection is logged as a security warning with the offending value

    Args:
        regex (Regex | str): The Regex pattern to validate against, or a raw
            pattern string (accepted for values stored by old migrations).
        message (Any | None): Custom validation error message.
        code (str | None): Error code for validation failures.
        inverse_match (bool | None): Match direction. Left unset (the default),
            or given any other truthy value, the value must match the regex; passing
            False requires the value not to match it.
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
        """Initialize the validator and configure the underlying RegexValidator.

        Args:
            regex (Regex | str): The Regex pattern to validate against, or a raw
                pattern string (accepted for values stored by old migrations).
            message (Any | None): Custom error message for validation failures.
            code (str | None): Error code for ValidationError exceptions.
            inverse_match (bool | None): Match direction. Left unset (the default),
                or given any other truthy value, the value must match the regex;
                passing False requires the value not to match it.
            flags (RegexFlag | None): Regex compilation flags for pattern matching.
            deny_injections (bool): Enable injection attack detection (default: False).
        """
        self.deny_injections = deny_injections
        # isinstance verification is needed to keep compatibility with old database migrations
        super().__init__(regex.value if isinstance(regex, Regex) else regex, message, code, inverse_match, flags)

    def __call__(self, value: str | None) -> None:
        """Validate a value against the configured regex and injection rules.

        Rejects a missing or empty value first. Then checks the value against the
        configured regex (requiring a match or a non-match depending on
        inverse_match) and, if deny_injections is enabled, also rejects it when it
        contains an injection character or a sensitive environment-variable
        assignment. Every rejection is logged as a warning describing the value as
        not matching the allowed regex, even when the actual cause was one of the
        injection checks.

        Args:
            value (str | None): The input value to validate.

        Raises:
            ValidationError: If the value is empty, fails the regex check, or is
                rejected by the injection checks while deny_injections is enabled.
        """
        if not value:
            raise ValidationError("Value is required", code=self.code, params={"value": value})
        regex_matches = re.fullmatch(self.regex, value)
        if (
            (self.inverse_match and not bool(regex_matches))
            or (not self.inverse_match and bool(regex_matches))
            or (
                self.deny_injections
                and (
                    bool(re.findall(Regex.INJECTION.value, value))
                    # Reject values that embed a sensitive environment variable
                    # assignment (e.g. LD_PRELOAD=...) which could hijack a tool
                    # subprocess when the value is rendered before the command
                    or bool(re.search(Regex.SENSITIVE_ENV.value, value))
                )
            )
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
    """Enforces password complexity requirements.

    Requires a minimum length and at least one character from each of the
    lowercase, uppercase, digit, and non-alphanumeric classes. This validator
    is compatible with Django's password validation framework, so it can be
    registered as one of the AUTH_PASSWORD_VALIDATORS.

    Security Requirements:
        - Minimum 12 characters length
        - At least one lowercase letter (a-z)
        - At least one uppercase letter (A-Z)
        - At least one digit (0-9)
        - At least one non-alphanumeric character, matched via \\W (this also
          accepts whitespace, and excludes underscore since it counts as a word
          character)

    Attributes:
        full_match (str): Combined length and allowed-character-class pattern
            that the whole password must match
        lowercase (str): Pattern requiring at least one lowercase letter
        uppercase (str): Pattern requiring at least one uppercase letter
        digit (str): Pattern requiring at least one digit
        symbol (str): Pattern requiring at least one non-word character (\\W)
    """

    # Underscore is a word character, so it isn't covered by \W or by the explicit
    # ranges below; a password containing one always fails this full match
    full_match = r"[A-Za-z0-9\W]{12,}"  # Full match with all requirements
    lowercase = r"[a-z]"  # At least one lowercase
    uppercase = r"[A-Z]"  # At least one uppercase
    digit = r"[0-9]"  # At least one digit
    symbol = r"[\W]"  # At least one symbol

    def validate(self, password: str, user: Any = None) -> None:
        """Validate password against security requirements.

        Checks the combined length and character-class pattern first; if it
        fails, raises the generic help text. Otherwise checks each character
        class individually and raises a message naming the first one missing.

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
