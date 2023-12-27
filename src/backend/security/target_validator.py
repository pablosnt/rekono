import ipaddress
import re
from re import RegexFlag
from typing import Any, List

from django.core.validators import RegexValidator
from django.forms import ValidationError
from target_blacklist.models import TargetBlacklist


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

    def __call__(self, value: str | None) -> None:
        super().__call__(value)
        blacklist = TargetBlacklist.objects.all().values_list("target", flat=True)
        if value in blacklist:
            raise ValidationError(
                f"Target is disallowed by policy",
                code=self.code,
                params={"value": value},
            )
        for denied_value in blacklist:
            try:
                match = re.fullmatch(denied_value, value)
            except:
                match = None
            if match:
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
