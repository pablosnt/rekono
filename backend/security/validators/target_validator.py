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
        - Regex pattern matching for flexible target specification
        - IPv4/IPv6 network range validation and blocking
        - Resilient matching that cannot be crashed by a malformed deny list
          entry (invalid regex or network)

    Validation Process:
        1. Basic regex pattern validation
        2. Deny list matching of the literal target (exact, regex and IP network)
        3. DNS resolution of the target and matching of the resolved values
        4. Comprehensive error handling and reporting

    Args:
        regex (Any): Regex pattern for target format validation.
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

    def __call__(self, value: str | None) -> None:
        """Validate target against regex patterns and deny lists.

        Performs comprehensive target validation including regex pattern matching,
        deny list checking (exact, regex pattern and IP network), and DNS-aware
        checking of the values the target resolves to. The target is normalized
        (lower-cased and trailing-dot stripped) before matching, and a domain is
        forward-resolved while a single IP is reverse-resolved so the resolved
        values are checked against the deny list too. Resolution is skipped while
        testing to keep validation deterministic and free of network dependencies.
        When an entry denies the target, its blocked counter is incremented to track
        how often each deny list entry is enforced.

        Args:
            value (str | None): The target to validate (IP, domain, URL, etc.).

        Raises:
            ValidationError: If target is invalid, missing, or denied by policy.
        """
        super().__call__(value)
        if not value:
            raise ValidationError("Target is required", code=self.code, params={"value": value})
        candidates = set([value])
        if not CONFIG.testing:  # pragma: no cover
            from targets.models import Target

            # Resolution errors must not block validation
            try:
                target_type = Target.get_type(value)
                if target_type in [TargetType.PRIVATE_IP, TargetType.PUBLIC_IP]:
                    resolved_domain, _, _ = socket.gethostbyaddr(value)
                    if resolved_domain:
                        candidates.add(resolved_domain)
                elif target_type == TargetType.DOMAIN:
                    _, _, addresses = socket.gethostbyname_ex(value)
                    candidates.update(addresses)
            except Exception:
                pass
        for _candidate in candidates:
            if not _candidate:
                continue
            # Strip a trailing dot so the FQDN form (example.com.) cannot bypass an
            # entry stored without it, since DNS treats both as equivalent
            candidate = _candidate.strip().rstrip(".").lower()
            for denied_value in TargetDenylist.objects.all():
                denied_target = denied_value.target.lower()
                # A malformed deny list entry must be ignored
                if candidate == denied_target:
                    denied_value.blocked = F("blocked") + 1
                    denied_value.save(update_fields=["blocked"])
                    self.logger.warning(f"[Security] Target '{value}' is denied by policy")
                    raise ValidationError(self.message, code=self.code, params={"value": value})
                try:
                    regex_match = bool(re.fullmatch(denied_target, candidate))
                except Exception:
                    regex_match = False
                if regex_match:
                    denied_value.blocked = F("blocked") + 1
                    denied_value.save(update_fields=["blocked"])
                    self.logger.warning(f"[Security] Target '{value}' match the denied value {denied_value.target}")
                    raise ValidationError(self.message, code=self.code, params={"value": value})
                for address_class, network_class in [
                    (ipaddress.IPv4Address, ipaddress.IPv4Network),
                    (ipaddress.IPv6Address, ipaddress.IPv6Network),
                ]:
                    # ValueError covers AddressValueError and NetmaskValueError so a
                    # malformed deny list network entry is ignored instead of crashing
                    try:
                        network_match = address_class(candidate) in network_class(denied_target)
                    except Exception:
                        network_match = False
                    if network_match:
                        denied_value.blocked = F("blocked") + 1
                        denied_value.save(update_fields=["blocked"])
                        self.logger.warning(
                            f"[Security] Target '{value}' belongs to the denied network {denied_value.target}"
                        )
                        raise ValidationError(self.message, code=self.code, params={"value": value})
