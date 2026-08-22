"""Validators applied to the values that the users send to Rekono.

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
    """Validator that requires a value to fully match one of the Rekono patterns.

    It replaces the call logic of the Django RegexValidator: an empty value is
    always rejected, the match must cover the whole value, and every rejection is
    logged as a security event.

    Attributes:
        deny_injections: Whether the value is also checked against the injection
          patterns, which the fields that reach a tool command line need.
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
        """Prepare the validator with the pattern that the values must match.

        Args:
            regex: The Regex pattern to validate against, or a raw pattern string
              (accepted for values stored by old migrations).
            message: Error message reported when a value is rejected.
            code: Error code of the raised validation errors.
            inverse_match: Match direction. Left unset (the default), or given any
              other truthy value, the value must match the regex; passing False
              requires the value not to match it.
            flags: Regex compilation flags.
            deny_injections: Whether to also reject the values that contain
              injection characters or a sensitive environment variable assignment.
        """
        self.deny_injections = deny_injections
        # isinstance verification is needed to keep compatibility with old database migrations
        super().__init__(regex.value if isinstance(regex, Regex) else regex, message, code, inverse_match, flags)

    def __call__(self, value: str | None) -> None:
        """Validate a value against the configured regex and injection rules.

        Every rejection is logged as a warning describing the value as not matching
        the allowed regex, even when the actual cause was one of the injection checks.

        Args:
            value: Value sent by the user, which can't be empty.

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
    """Validator for the datetime fields that can only hold a future value."""

    def __call__(self, value: Any) -> None:
        """Validate that a datetime is in the future.

        Args:
            value: Datetime sent by the user.

        Raises:
            ValidationError: If the datetime is in the past or is right now.
        """
        if value <= timezone.now():
            raise ValidationError("Datetime must be future", code=self.code)


class PasswordValidator:
    """Complexity policy that the Rekono passwords must satisfy.

    Requires at least 12 characters, including a lowercase letter, an uppercase
    one, a digit, and a symbol. It's registered as one of the Django
    AUTH_PASSWORD_VALIDATORS, so it applies wherever a password is set.

    Attributes:
        full_match: Length and accepted characters that the whole password must match.
        lowercase: Pattern that finds a lowercase letter.
        uppercase: Pattern that finds an uppercase letter.
        digit: Pattern that finds a digit.
        symbol: Pattern that finds a symbol, which also accepts whitespace.
    """

    # Underscore is a word character, so it isn't covered by \W or by the explicit
    # ranges below; a password containing one always fails this full match
    full_match = r"[A-Za-z0-9\W]{12,}"
    lowercase = r"[a-z]"
    uppercase = r"[A-Z]"
    digit = r"[0-9]"
    symbol = r"[\W]"

    def validate(self, password: str, user: Any = None) -> None:
        """Check that a password satisfies the complexity policy.

        Args:
            password: Password to be checked.
            user: User that the password belongs to, required by the Django
              validator interface but not needed by this policy.

        Raises:
            ValidationError: With the generic help text if the password is too short
              or contains a character that isn't accepted, and naming the missing
              character class otherwise.
        """
        if not bool(re.fullmatch(self.full_match, password)):
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
        """Return the description of the password policy shown to the users."""
        return "Your password must contain at least 1 lowercase, 1 uppercase, 1 digit and 1 symbol"
