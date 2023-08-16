import ipaddress
import logging
import re
from enum import Enum
from re import RegexFlag
from typing import Any

from django.core.validators import RegexValidator
from django.forms import ValidationError
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
        self.target_blacklist = CONFIG.base_target_blacklist
        settings = Settings.objects.filter(pk=1)
        if settings.exists():
            self.target_blacklist += StringAsListField().to_representation(
                settings.first().target_blacklist
            )

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
