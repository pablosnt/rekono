"""Validation of the targets that Rekono is allowed to scan.

Besides checking the format of an IP address, IP range, network, domain, or URL,
the validator enforces the target denylist, which is what keeps the scans away from
the hosts that must never be tested.
"""

import ipaddress
import re
import socket
from re import RegexFlag
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import F

from framework.logging import LoggingEntity
from rekono.settings import CONFIG
from security.validators.enums import Regex
from target_denylist.models import TargetDenylist
from targets.enums import TargetType


class TargetValidator(RegexValidator, LoggingEntity):
    """Validator that rejects the targets denied by the target denylist.

    A target is denied when it matches an entry of the denylist by itself or
    through any of the other ways of reaching the same host: the addresses of an IP
    range, the IPv4 form of an IPv4-mapped IPv6 address, the addresses that a domain
    resolves to, and the domain that an address resolves to. A malformed denylist
    entry is ignored instead of crashing the validation, so one bad entry can't
    block every scan.

    Attributes:
        code: Error code of the raised validation errors.
    """

    def __init__(
        self,
        regex: Regex | str,
        message: Any | None = "Target is disallowed by policy",
        code: str | None = "target",
        inverse_match: bool | None = False,
        flags: RegexFlag | None = None,
    ) -> None:
        """Prepare the validator with the pattern that the targets must match.

        Args:
            regex: The Regex pattern to validate the format of the targets against,
                or a raw pattern string (accepted for values stored by old migrations).
            message: Error message reported when a target is rejected.
            code: Error code of the raised validation errors.
            inverse_match: Whether the targets must not match the regex.
            flags: Regex compilation flags.
        """
        self.code = code
        # isinstance verification is needed to keep compatibility with old database migrations
        super().__init__(regex.value if isinstance(regex, Regex) else regex, message, code, inverse_match, flags)

    def _deny(self, value: str, denied_target: TargetDenylist, reason: str) -> None:
        """Reject a target that matched a deny list entry.

        F() increments the entry's blocked counter at the database level, so concurrent
        validations hitting the same entry don't lose updates to a race condition.

        Args:
            value: The target being validated.
            denied_target: Denylist entry matched by the target.
            reason: How the target matched the entry, used to build the log message.

        Raises:
            ValidationError: Always, since reaching this method means the target is denied.
        """
        denied_target.blocked = F("blocked") + 1
        denied_target.save(update_fields=["blocked"])
        self.logger.warning(f"[Security] Target '{value}' {reason} {denied_target.target}")
        raise ValidationError(self.message, code=self.code, params={"value": value})

    @staticmethod
    def get_ip_range_addresses(ip_range: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
        """Expand an IP range into every address that it covers.

        Ranges are written as "10.10.30.1-50", where the value after the dash is only
        the last octet of the final address, so it is completed with the network part
        of the first one before iterating over the addresses in between. The IP range
        pattern only checks the shape of the value, so both ends are parsed as addresses
        here to reject the ranges that it accepts but that cover no address, like the
        ones with octets over 255 or with a start greater than the end.

        It's a static method because it is also used by Target.get_type to tell a real
        IP range from a value that just looks like one.

        Args:
            ip_range: Range written as "10.10.30.1-50", where the value after the
              dash is only the last octet of the final address.

        Returns:
            All the addresses of the range, including both ends, or an empty list if it
            covers no address. Malformed values are reported as an empty list instead of
            an exception because denylist entries are expanded with this method too, and
            a malformed entry must be ignored instead of denying the target.
        """
        try:
            start, end = ip_range.rsplit("-", 1)
            network = start.rsplit(".", 1)[0]
            # Both ends are parsed to reject the ranges with octets over 255, like 10.10.30.1-999,
            # and summarize_address_range to reject the reversed ones, like 10.10.30.50-1, since it
            # raises ValueError for them. A reversed range would otherwise expand into an empty list
            first, last = ipaddress.ip_address(start), ipaddress.ip_address(f"{network}.{end}")
            ipaddress.summarize_address_range(first, last)
            return [ipaddress.ip_address(address) for address in range(int(first), int(last) + 1)]
        except Exception:
            return []

    def __call__(self, value: str | None) -> None:
        """Validate the format of a target and check it against the denylist.

        The target is first expanded into a set of candidates, since several ways of
        writing a target reach the same host: an IP range contributes all its
        addresses and an IPv4-mapped IPv6 address contributes its IPv4 form. A domain
        is also forward-resolved while a single IP is reverse-resolved, so the
        resolved values are checked against the denylist too. Resolution is skipped
        while testing to keep validation deterministic and free of network
        dependencies. Every candidate is normalized (lower-cased and trailing-dot
        stripped) and matched against each denylist entry, and the target is rejected
        as soon as one of them matches.

        Args:
            value: Target to validate, as an IP address, IP range, network, domain,
              or URL.

        Raises:
            ValidationError: If the target is missing, has an invalid format, or is
                denied by the target denylist.
        """
        super().__call__(value)
        if not value:
            raise ValidationError("Target is required", code=self.code, params={"value": value})
        candidates = set([value])

        from targets.models import Target

        try:
            target_type = Target.get_type(value)
        except Exception:
            target_type = None

        if target_type in [TargetType.PRIVATE_IP, TargetType.PUBLIC_IP]:
            ip = ipaddress.ip_address(value)
            # An IPv4-mapped IPv6 address reaches the same host as the IPv4 one that it maps, so
            # ::ffff:127.0.0.1 can't be used to reach a denied IPv4 address
            if ip.version == 6 and ip.ipv4_mapped:
                candidates.add(str(ip.ipv4_mapped))
        elif target_type == TargetType.IP_RANGE:
            candidates.update([str(ip) for ip in self.get_ip_range_addresses(value)])

        if not CONFIG.testing:  # pragma: no cover
            # Resolution errors must not block validation
            try:
                if target_type in [TargetType.PRIVATE_IP, TargetType.PUBLIC_IP]:
                    resolved_domain, _, _ = socket.gethostbyaddr(value)
                    if resolved_domain:
                        candidates.add(resolved_domain)
                elif target_type == TargetType.DOMAIN:
                    _, _, addresses = socket.gethostbyname_ex(value)
                    candidates.update(addresses)
            except Exception:
                pass
        denylist_entries = TargetDenylist.objects.all()
        for _candidate in candidates:
            if not _candidate:
                continue
            # Strip a trailing dot so the FQDN form (example.com.) cannot bypass an
            # entry stored without it, since DNS treats both as equivalent
            candidate = _candidate.strip().rstrip(".").lower()
            for denied_value in denylist_entries:
                denied_target = denied_value.target.lower()
                if candidate == denied_target:
                    self._deny(value, denied_value, "matches denied target")
                # A malformed deny list entry (invalid regex, IP range or network) must be
                # ignored instead of crashing validation
                try:
                    if bool(re.fullmatch(denied_value.target, candidate, re.IGNORECASE)):
                        self._deny(value, denied_value, "matches denied target pattern")
                    # A domain only matches an entry as a literal value or as a regex pattern,
                    # so the address-based comparisons are skipped for it
                    if target_type != TargetType.DOMAIN:
                        # An IP range entry denies every address it covers, so it is expanded
                        # before comparing it with the target
                        if bool(re.fullmatch(Regex.IP_RANGE.value, denied_target)):
                            denied_targets = self.get_ip_range_addresses(denied_target)
                            if target_type == TargetType.NETWORK:
                                target_network = ipaddress.ip_network(candidate)
                                if any(denied_target in target_network for denied_target in denied_targets):
                                    self._deny(value, denied_value, "is included in denied range")
                            else:
                                if ipaddress.ip_address(candidate) in denied_targets:
                                    self._deny(value, denied_value, "belongs to denied range")
                        if target_type == TargetType.NETWORK:
                            # A network covers several addresses, so it is compared to the denied network
                            # in both directions to detect also the networks that include it
                            if ipaddress.ip_network(candidate).overlaps(ipaddress.ip_network(denied_target)):
                                self._deny(value, denied_value, "overlaps denied network")
                        else:
                            if ipaddress.ip_address(candidate) in ipaddress.ip_network(denied_target):
                                self._deny(value, denied_value, "belongs to denied network")

                except Exception as ex:
                    # The rejections raised by _deny happen inside this block too, so they are
                    # re-raised instead of being ignored as a malformed deny list entry
                    if isinstance(ex, ValidationError):
                        raise ex
