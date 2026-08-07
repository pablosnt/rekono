"""Model of the targets that Rekono scans."""

import ipaddress
import re
import socket
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from framework.cache import Cache
from framework.enums import InputKeyword
from framework.models import BaseInput
from projects.models import Project
from security.validators.input_validator import Regex
from security.validators.target_validator import TargetValidator
from targets.enums import TargetType


class Target(BaseInput):
    """Host, network, or domain of a project that can be scanned.

    It's the first input of the executions, so the tools receive the target even
    before any finding has been reported for it.

    Attributes:
        project: Project that the target belongs to.
        target: Value of the target, which is validated against the denylist.
        type: Kind of target, detected from its value when it's created.
    """

    project = models.ForeignKey(Project, related_name="targets", on_delete=models.CASCADE)
    target = models.TextField(max_length=100, validators=[TargetValidator(Regex.TARGET)])
    type = models.TextField(max_length=10, choices=TargetType.choices)

    _filters = [BaseInput.Filter(type=TargetType, field="type")]
    _parse_mapping = {
        InputKeyword.TARGET: "target",
        InputKeyword.HOST: "target",
        InputKeyword.URL: lambda instance, task: instance.get_url(instance.target, task=task),
    }
    _project_field = "project"
    _dns_cache = Cache(prefix="dns")

    class Meta:
        """Model configuration, allowing each target to be defined once per project."""

        constraints = [models.UniqueConstraint(fields=["project", "target"], name="unique_target")]

    @classmethod
    def get_type(cls, target: str) -> str:
        """Detect the type of a target from its value.

        The IP ranges are expanded, and the domains are resolved, since both
        patterns accept values that don't identify any host.

        Args:
            target: Value written by the user, as an IP address, IP range,
              network, domain, or URL.

        Returns:
            The matching TargetType value, and never a plain string, so it can be
            assigned to the type field directly.

        Raises:
            ValidationError: If the value isn't a supported target, which also
                covers a domain that doesn't resolve.
        """
        try:
            ip = ipaddress.ip_address(target)
            if ip.is_private:
                return TargetType.PRIVATE_IP
            else:
                return TargetType.PUBLIC_IP
        except ValueError:
            pass
        try:
            ipaddress.ip_network(target)
            return TargetType.NETWORK
        except ValueError:
            pass
        if bool(re.fullmatch(Regex.IP_RANGE.value, target)) and len(TargetValidator.get_ip_range_addresses(target)) > 0:
            return TargetType.IP_RANGE
        if cls.resolve_domain(target) is not None:
            return TargetType.DOMAIN
        BaseInput.logger.warning(f"[Security] Invalid target {target}")
        raise ValidationError(
            "Invalid target. IP address, IP range or domain is required",
            code="target",
            params={"value": target},
        )

    def __str__(self) -> str:
        """Return the value of the target."""
        return self.target

    @classmethod
    def resolve_domain(cls, domain: str) -> str | None:
        """Forward-resolve a domain name to an IP address, with caching.

        Results are cached in Redis keyed by the domain, so a domain is resolved at most once
        per cache TTL. Shared by create_finding_from_user_input() and get_type() (a classmethod),
        which is why the cache logic lives here rather than on the instance. A single execution can produce
        hundreds of findings sharing the same target (e.g. every path Dirsearch discovers), and
        each would otherwise issue its own ``socket.gethostbyname`` call; caching collapses them
        into a single lookup and keeps that burst from overwhelming the resolver.

        Args:
            domain: Domain name to resolve.

        Returns:
            The resolved IP address, or None when resolution fails, so callers can
            treat the name as unresolvable instead of propagating the error.
        """
        cached = cls._dns_cache.get(domain)
        if cached:
            return cached
        try:
            ip = socket.gethostbyname(domain)
        except socket.gaierror:
            # Do not cache failures not to suppress later resolutions
            return None
        cls._dns_cache.set(domain, ip)
        return ip

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        """Create the host finding equivalent to this target.

        Args:
            execution: Execution that the created finding belongs to.
            **fields: Extra values for the finding, unused because a target only
              provides the host itself.

        Returns:
            The new host finding, or None for the targets that don't identify one
            single host, like the networks and the IP ranges, and for the domains
            that can't be resolved.
        """
        from findings.models import Host

        if self.type == TargetType.DOMAIN:
            ip = self.resolve_domain(self.target)
            if not ip:
                return None
            fields["ip"] = ip
            fields["domain"] = self.target
        elif self.type in [TargetType.PRIVATE_IP, TargetType.PUBLIC_IP]:
            fields["ip"] = self.target
        else:
            return None
        return Host.objects.create_finding(execution, **{**fields, "created_from_user_input": True})
