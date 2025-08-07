import re
from enum import Enum
from re import RegexFlag
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

from framework.logging import LoggingEntity


class Regex(Enum):
    IP_RANGE = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}"
    NAME = r"[\wÀ-ÿ\s\.:\-\[\]()@]{0,120}"
    TEXT = r"[^;<>]*"
    TARGET = r"[\w\d\.:\-/]{1,100}"
    TARGET_REGEX = r"[\w\d\.,:\-/\*\?\+\(\)\\]{1,300}"
    PATH = r"[\w\.\-_/\\]{0,500}"
    PATH_WITH_QUERYPARAMS = r"[\w\.\-_/\\#?&%$]{0,500}"
    CVE = r"CVE-\d{4}-\d{1,7}"
    SECRET = r"[\w\s\./\-=\+,:<>¿?¡!#&$()@%\[\]\{\}\*]{1,500}"
    INJECTION = r"[;\"'&<>$]+"


class Validator(RegexValidator, LoggingEntity):
    def __init__(
        self,
        regex: Regex,
        message: Any | None = "Provided value contains disallowed characters",
        code: str | None = None,
        inverse_match: bool | None = ...,  # type: ignore
        flags: RegexFlag | None = None,
        deny_injections: bool = False,
    ) -> None:
        self.deny_injections = deny_injections
        super().__init__(regex.value, message, code, inverse_match, flags)

    def __call__(self, value: str | None) -> None:
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
    def __call__(self, value: Any) -> None:
        if value <= timezone.now():
            raise ValidationError("Datetime must be future", code=self.code)


class PasswordValidator:
    full_match = r"[A-Za-z0-9\W]{12,}"  # Full match with all requirements
    lowercase = r"[a-z]"  # At least one lowercase
    uppercase = r"[A-Z]"  # At least one uppercase
    digit = r"[0-9]"  # At least one digit
    symbol = r"[\W]"  # At least one symbol

    def validate(self, password: str, user: Any = None) -> None:
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
        return "Your password must contain at least 1 lowercase, 1 uppercase, 1 digit and 1 symbol"
