import ipaddress
import logging
import re
from dataclasses import dataclass
from enum import Enum
from re import RegexFlag
from typing import Any

from django.core.validators import RegexValidator
from django.forms import ValidationError
from django.utils import timezone
from framework.fields import StringAsListField
from rekono.settings import CONFIG
from settings.models import Settings

logger = logging.getLogger()


class Regex(Enum):
    IP_RANGE = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}"
    NAME = r"[\wÀ-ÿ\s\.\-\[\]()@]{0,120}"
    TEXT = r'[\wÀ-ÿ\s\.:,+\-\'"?¿¡!#%$€\[\]()]{0,300}'
    TARGET = r"[\w\d\.:\-/]{1,100}"
    TARGET_REGEX = r"[\w\d\.:\-/\.\*\?\+\(\)\\]{1,100}"
    PATH = r"[\w\.\-_/\\]{0,500}"
    PATH_WITH_QUERYPARAMS = r"[\w\.\-_/\\#?&%$]{0,500}"
    CVE = r"CVE-\d{4}-\d{1,7}"
    SECRET = r"[\w\./\-=\+,:<>¿?¡!#&$()@%\[\]\{\}\*]{1,500}"


class Validator(RegexValidator):
    def __init__(
        self,
        regex: Any | None = ...,
        message: Any | None = ...,
        code: str | None = ...,
        inverse_match: bool | None = ...,
        flags: RegexFlag | None = ...,
    ) -> None:
        message = "Provided value contains disallowed characters"
        flags = None  # Needed to prevent TypeError
        super().__init__(regex, message, code, inverse_match, flags)

    def __call__(self, value: str | None) -> None:
        regex_matches = re.fullmatch(self.regex, value)
        invalid_input = (
            not bool(regex_matches) if self.inverse_match else bool(regex_matches)
        )
        if invalid_input:
            logger.warning(
                f"[Security] Invalid value that doesn't match the regex '{self.regex}'"
            )
            raise ValidationError(self.message, code=self.code, params={"value": value})


class TargetValidator(RegexValidator):
    def __init__(
        self,
        regex: Any | None = ...,
        message: Any | None = ...,
        code: str | None = "target",
        inverse_match: bool | None = False,
        flags: RegexFlag | None = None,
    ) -> None:
        self.code = code
        flags = None  # Needed to prevent TypeError
        super().__init__(regex, message, code, inverse_match, flags)
        self.target_blacklist = CONFIG.target_blacklist
        try:
            settings = Settings.objects.first()
            if settings.exists():
                self.target_blacklist += StringAsListField().to_representation(
                    settings.first().target_blacklist
                )
        except:
            pass

    def __call__(self, value: str | None) -> None:
        super().__call__(value)
        if value in self.target_blacklist:
            raise ValidationError(
                f"Target is disallowed by policy",
                code=self.code,
                params={"value": value},
            )
        for denied_value in self.target_blacklist:
            if re.fullmatch(denied_value, value):
                raise ValidationError(
                    f"Target is disallowed by policy",
                    code=self.code,
                    params={"value": value},
                )
            for address_class, network_class in [
                (ipaddress.IPv4Address, ipaddress.IPv4Network),
                (ipaddress.IPv6Address, ipaddress.IPv6Network),
            ]:
                try:
                    address = address_class(value)
                    network = network_class(denied_value)
                    if address in network:
                        raise ValidationError(
                            f"Target belongs to a network that is disallowed by policy",
                            code="target",
                            params={"value": value},
                        )
                except ipaddress.AddressValueError:
                    pass


@dataclass
class TimeValidator:
    code: str
    # TODO: Remove
    # def __init__(self, code: str):
    #     self.code = code

    def future_datetime(self, datetime: Any) -> None:
        if datetime <= timezone.now():
            raise ValidationError("Datetime must be future", code=self.code)

    def time_amount(self, amount: int) -> None:
        if amount > 1000 or amount <= 0:
            raise ValidationError("Time value is too high", code=self.code)


class PasswordValidator:
    """Rekono password complexity validator."""

    full_match = r"[A-Za-z0-9\W]{12,}"  # Full match with all requirements
    lowercase = r"[a-z]"  # At least one lowercase
    uppercase = r"[A-Z]"  # At least one uppercase
    digits = r"[0-9]"  # At least one digit
    symbols = r"[\W]"  # At least one symbol
    message = "Your password must contain at least 1 lowercase, 1 uppercase, 1 digit and 1 symbol"

    def validate(self, password: str, user: Any = None) -> None:
        """Validate if password match the complexity requirements.

        Args:
            password (str): Password to check
            user (User, optional): User that is establishing the password. Defaults to None.

        Raises:
            ValidationError: Raised if password doesn't match the complexity requirements
        """
        if not bool(re.fullmatch(self.full_match, password)):  # Full check
            raise ValidationError(self.message)
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
        return self.message
