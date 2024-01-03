import logging
import re
from enum import Enum
from re import RegexFlag
from typing import Any

from django.core.validators import RegexValidator
from django.forms import ValidationError
from django.utils import timezone

logger = logging.getLogger()


class Regex(Enum):
    IP_RANGE = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}"
    NAME = r"[\wÀ-ÿ\s\.\-\[\]()@]{0,120}"
    TEXT = r"[^;<>/]*"
    TARGET = r"[\w\d\.:\-/]{1,100}"
    TARGET_REGEX = r"[\w\d\.,:\-/\.\*\?\+\(\)\\]{1,300}"
    PATH = r"[\w\.\-_/\\]{0,500}"
    PATH_WITH_QUERYPARAMS = r"[\w\.\-_/\\#?&%$]{0,500}"
    CVE = r"CVE-\d{4}-\d{1,7}"
    SECRET = r"[\w\./\-=\+,:<>¿?¡!#&$()@%\[\]\{\}\*]{1,500}"


class Validator(RegexValidator):
    def __init__(
        self,
        regex: Any | None,
        message: Any | None = "Provided value contains disallowed characters",
        code: str | None = None,
        inverse_match: bool | None = ...,  # type: ignore
        flags: RegexFlag | None = None,
    ) -> None:
        super().__init__(regex, message, code, inverse_match, flags)

    def __call__(self, value: str | None) -> None:
        if not value:
            raise ValidationError(
                "Value is required", code=self.code, params={"value": value}
            )
        regex_matches = re.fullmatch(self.regex, value)
        invalid_input = (
            not bool(regex_matches) if self.inverse_match else bool(regex_matches)
        )
        if invalid_input:
            logger.warning(
                f"[Security] Invalid value that doesn't match the regex '{self.regex}'"
            )
            raise ValidationError(self.message, code=self.code, params={"value": value})


class FutureDatetimeValidator(RegexValidator):
    def __call__(self, value: Any) -> None:
        if value <= timezone.now():
            raise ValidationError("Datetime must be future", code=self.code)


class TimeAmountValidator(RegexValidator):
    def __call__(self, value: int) -> None:
        if value > 1000 or value <= 0:
            raise ValidationError("Time value is too high", code=self.code)


class PasswordValidator:
    """Rekono password complexity validator."""

    full_match = r"[A-Za-z0-9\W]{12,}"  # Full match with all requirements
    lowercase = r"[a-z]"  # At least one lowercase
    uppercase = r"[A-Z]"  # At least one uppercase
    digits = r"[0-9]"  # At least one digit
    symbols = r"[\W]"  # At least one symbol

    def validate(self, password: str, user: Any = None) -> None:
        """Validate if password match the complexity requirements.

        Args:
            password (str): Password to check
            user (User, optional): User that is establishing the password. Defaults to None.

        Raises:
            ValidationError: Raised if password doesn't match the complexity requirements
        """
        if not bool(re.fullmatch(self.full_match, password)):  # Full check
            raise ValidationError(self.get_help_text())
        if not bool(re.search(self.lowercase, password)):  # Lower case check
            raise ValidationError("Your password must contain at least 1 lowercase")
        if not bool(re.search(self.uppercase, password)):  # Upper case check
            raise ValidationError("Your password must contain at least 1 uppercase")
        if not bool(re.search(self.digits, password)):  # Digits check
            raise ValidationError("Your password must contain at least 1 digit")
        if not bool(re.search(self.symbols, password)):  # Symbols check
            raise ValidationError("Your password must contain at least 1 symbol")

    def get_help_text(self) -> str:
        """Get help message.

        Returns:
            str: Help message
        """
        return "Your password must contain at least 1 lowercase, 1 uppercase, 1 digit and 1 symbol"
