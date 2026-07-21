"""Host metadata enrichment platform integration.

Provides automated host metadata enrichment including DNS resolution,
geolocation services, and network intelligence gathering for discovered
host findings during security assessments.
"""

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
    """Integration class for host metadata enrichment and intelligence gathering.

    Automatically enriches host findings with additional metadata including
    DNS reverse resolution for domain names and geolocation information for
    public IP addresses using external geolocation services.

    Attributes:
        finding_types (list): List of finding types processed by this integration (Host)
    """

    finding_types = [Host]

    def is_enabled(self) -> bool:
        """Check if host metadata enrichment integration is enabled.

        This integration is always enabled as it provides core metadata
        enrichment functionality without external API dependencies.

        Returns:
            bool: Always returns True for this integration
        """
        return True

    def _process_finding(self, execution: Execution, finding: Finding) -> None:
        """Process and enrich host finding with metadata and geolocation information.

        Performs DNS reverse resolution to discover hostnames and queries geolocation
        services for public IP addresses to gather geographic intelligence including
        country, city, and coordinate information.

        Args:
            execution (Execution): The execution context for this processing
            finding (Finding): The host finding to enrich with metadata
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
