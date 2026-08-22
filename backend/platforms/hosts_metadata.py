"""Integration that completes the hosts with their name and their location."""

import socket
import warnings

from executions.models import Execution
from findings.models import Finding, Host
from framework.platforms import BaseIntegration
from targets.enums import TargetType
from targets.models import Target

# geocoder emits SyntaxWarnings on import, so they are silenced before importing it
warnings.filterwarnings("ignore", category=SyntaxWarning, module=r".*geocoder.*")

import geocoder  # noqa: E402


class HostsMetadata(BaseIntegration):
    """Integration that resolves the domain of a host and where it's located.

    Attributes:
        finding_types: Only the hosts have a domain and a location.
    """

    finding_types = [Host]

    def is_enabled(self) -> bool:
        """Check if this platform must be used.

        Returns:
            Always true, since this is the only platform without an integration
            that the users can disable: resolving a host is part of discovering it.
        """
        return True

    def _process_finding(self, execution: Execution, finding: Finding) -> None:
        """Complete a discovered host with its domain and its location.

        Args:
            execution: Execution that discovered the host.
            finding: Host to complete.
        """
        ip_type = Target.get_type(finding.ip)
        update = []
        if finding.domain is None and ip_type in [TargetType.PRIVATE_IP, TargetType.PUBLIC_IP]:
            try:
                finding.domain = socket.gethostbyaddr(finding.ip)[0]
                update.append("domain")
            except Exception:
                pass
        if ip_type == TargetType.PUBLIC_IP and not all(
            [finding.country, finding.city, finding.latitude, finding.longitude]
        ):
            geocode = geocoder.ip(finding.ip)
            if geocode and geocode.ok:
                finding.country = geocode.country
                finding.city = geocode.city
                finding.latitude, finding.longitude = geocode.latlng
                update.extend(["country", "city", "latitude", "longitude"])
        if update:
            finding.save(update_fields=update)
