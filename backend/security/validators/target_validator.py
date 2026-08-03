"""Target validation utilities for security testing workflows.

Provides specialized validation for penetration testing targets including
IP addresses, networks, domains, and URLs. This module implements security
controls to prevent testing of unauthorized or restricted targets through
configurable deny lists and policy enforcement.
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
    """Validator for penetration testing targets with deny list enforcement.

    Validates security testing targets against both regex patterns and
    configurable deny lists to prevent unauthorized testing. Supports
    validation of IP addresses, networks, domains, and regex patterns.

    Security Features:
        - Deny list enforcement for restricted targets
        - Target normalization (lower-casing and trailing-dot stripping) so
          case and trailing-dot variants cannot bypass a denied entry
        - DNS-aware checks: domains are forward-resolved and their addresses
          checked, single IPs are reverse-resolved and their hostname checked,
          so a target cannot reach a denied address through name resolution
        - IPv4-mapped IPv6 addresses checked as their IPv4 form, since both
          reach the same host
        - IP range targets checked address by address, and IP range deny list
          entries expanded so they deny both the addresses they cover and the
          networks that contain any of them
        - Regex pattern matching for flexible target specification
        - IPv4/IPv6 network validation and blocking, comparing networks in both
          directions so a network that contains a denied one is denied as well
        - Resilient matching that cannot be crashed by a malformed deny list
          entry (invalid regex, IP range or network)

    Validation Process:
        1. Basic regex pattern validation
        2. Expansion of the target into a candidate set: the literal value, the
           addresses of an IP range, the IPv4 form of an IPv4-mapped IPv6 address,
           and the values obtained from DNS resolution
        3. Deny list matching of every candidate (exact, regex, IP range and
           network), rejecting the target as soon as any one of them matches

    Args:
        regex (Regex | str): Regex pattern for target format validation.
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

    def _deny(self, value: str, denied_target: TargetDenylist, reason: str) -> None:
        """Reject a target that matched a deny list entry.

        F() increments the entry's blocked counter at the database level, so concurrent
        validations hitting the same entry don't lose updates to a race condition.

        Args:
            value (str): The target being validated.
            denied_target (TargetDenylist): Deny list entry matched by the target.
            reason (str): How the target matched the entry, used to build the log message.

        Raises:
            ValidationError: Always, since reaching this method means the target is denied.
        """
        denied_target.blocked = F("blocked") + 1
        denied_target.save(update_fields=["blocked"])
        self.logger.warning(f"[Security] Target '{value}' {reason} {denied_target.target}")
        raise ValidationError(self.message, code=self.code, params={"value": value})

    def get_ip_range_addresses(self, ip_range: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
        """Expand an IP range into every address that it covers.

        Ranges are written as "10.10.30.1-50", where the value after the dash is only
        the last octet of the final address, so it is completed with the network part
        of the first one before iterating over the addresses in between.

        Args:
            ip_range (str): IP range to expand.

        Returns:
            list[ipaddress.IPv4Address | ipaddress.IPv6Address]: All the addresses of
            the range, including both ends.
        """
        start, end = ip_range.rsplit("-", 1)
        network = start.rsplit(".", 1)[0]
        first, last = ipaddress.ip_address(start), ipaddress.ip_address(f"{network}.{end}")
        return [ipaddress.ip_address(ip) for ip in range(int(first), int(last) + 1)]

    def __call__(self, value: str | None) -> None:
        """Validate target against regex patterns and deny lists.

        Performs comprehensive target validation including regex pattern matching,
        deny list checking (exact, regex pattern, IP range and network), and DNS-aware
        checking of the values the target resolves to. The target is first expanded
        into a set of candidates, since several ways of writing a target reach the
        same host: an IP range contributes all its addresses and an IPv4-mapped IPv6
        address contributes its IPv4 form. A domain is also forward-resolved while a
        single IP is reverse-resolved, so the resolved values are checked against the
        deny list too. Resolution is skipped while testing to keep validation
        deterministic and free of network dependencies. Every candidate is normalized
        (lower-cased and trailing-dot stripped) and matched against each deny list
        entry, and the target is rejected as soon as one of them matches. When an
        entry denies the target, its blocked counter is incremented to track how
        often each deny list entry is enforced.

        Args:
            value (str | None): The target to validate (IP, domain, URL, etc.).

        Raises:
            ValidationError: If target is invalid, missing, or denied by policy.
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
                    if bool(re.fullmatch(denied_target, candidate)):
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
