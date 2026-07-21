"""VirusTotal threat intelligence platform integration for host reputation analysis.

This module provides the core integration class for the VirusTotal threat intelligence
platform, enabling real-time reputation analysis, malware detection, and threat
assessment for discovered hosts and domains. The integration automatically processes
Host findings to enrich them with comprehensive threat intelligence data.
"""

from typing import Any, Callable

from executions.models import Execution
from findings.models import Host
from framework.platforms import BaseIntegration
from platforms.virustotal.models import VirusTotalSettings
from targets.enums import TargetType
from targets.models import Target


class VirusTotal(BaseIntegration):
    """VirusTotal threat intelligence platform integration.

    Provides comprehensive integration with the VirusTotal API for real-time
    threat intelligence gathering, reputation analysis, and malware detection
    for discovered hosts and domains. Automatically enriches Host findings
    with reputation scores, voting data, and WHOIS information.

    Attributes:
        finding_types (list): Supported finding types (Host only)
        url (str): VirusTotal API v3 base endpoint URL

    Features:
        - Real-time reputation analysis for IP addresses and domains
        - Malicious/harmless vote data collection for risk assessment
        - WHOIS data enrichment for domain investigation
        - Public IP address threat intelligence gathering
        - Automated finding processing with error handling
        - Rate limiting compliance with VirusTotal API restrictions
    """

    finding_types = [Host]
    url = "https://www.virustotal.com/api/v3/"

    @property
    def settings(self) -> VirusTotalSettings:
        """Get VirusTotal platform configuration settings from database.

        Returns:
            VirusTotalSettings: Platform configuration instance or None if not configured.
        """
        return VirusTotalSettings.objects.first()

    def is_available(self) -> bool:
        """Check if the VirusTotal platform is available and accessible.

        Returns the availability status stored in the database, which is updated
        each time the platform settings are saved.

        Returns:
            bool: True if the platform is available and accessible, False otherwise.
        """
        return self.settings.is_available

    def live_is_available(self) -> bool:
        """Check if the VirusTotal platform is available and accessible.

        Validates platform connectivity by checking for valid API credentials
        and performing a test API request to the VirusTotal service.

        Returns:
            bool: True if the platform is available and accessible, False otherwise.
        """
        if self.settings.secret is None:
            return False
        try:
            self._request(self.session.get, "ip_addresses/8.8.8.8")
            return True
        except Exception:
            return False

    def _request(
        self, method: Callable, url: str, json: bool = True, trigger_exception: bool = True, **kwargs: Any
    ):  # pragma: no cover
        """Make authenticated HTTP request to VirusTotal API.

        Constructs and executes authenticated HTTP requests to the VirusTotal API
        with proper headers, authentication, and error handling.

        Args:
            method (Callable): HTTP method to use (GET, POST, etc.)
            url (str): API endpoint URL relative to base URL
            json (bool): Whether to parse response as JSON. Defaults to True.
            trigger_exception (bool): Whether to raise exceptions on errors. Defaults to True.
            **kwargs: Additional keyword arguments passed to the request method

        Returns:
            Any: API response data, typically JSON parsed to Python objects
        """
        return super()._request(
            method,
            f"{self.url}{url}",
            json,
            trigger_exception,
            **{**kwargs, "headers": {"accept": "application/json", "x-apikey": self.settings.secret}},
        )

    def is_finding_processable(self, finding: Host) -> bool:
        """Determine if a Host finding should be processed for threat intelligence.

        Only hosts on a public IP are processed. A host on a private network is
        skipped because its IP or domain would be an internal address or hostname
        that must not be leaked to VirusTotal.

        Args:
            finding (Host): The Host finding to evaluate for processing

        Returns:
            bool: True if the finding should be processed, False otherwise
        """
        # The IP type is the only gate: never send anything (IP or domain) for a host on a private
        # network, since its domain would be an internal hostname that we must not leak to VirusTotal
        return super().is_finding_processable(finding) and Target.get_type(finding.ip) is TargetType.PUBLIC_IP

    def _process_finding(self, execution: Execution, finding: Host) -> None:
        """Process a Host finding by enriching it with VirusTotal threat intelligence.

        Queries the VirusTotal API to gather threat intelligence data for the
        given Host finding, including reputation scores, voting data, and WHOIS
        information. Updates the finding with the collected intelligence data.

        Args:
            execution (Execution): The execution that produced the finding
            finding (Host): The Host finding to enrich with threat intelligence
        """
        try:
            if finding.domain is not None:
                data = self._request(self.session.get, f"domains/{finding.domain}")
            else:
                data = self._request(self.session.get, f"ip_addresses/{finding.ip}")
            data = data.get("data", {}).get("attributes", {})
            finding.reputation = data.get("reputation")
            stats = data.get("last_analysis_stats", {})
            finding.malicious_analysis = stats.get("malicious", 0)
            finding.suspicious_analysis = stats.get("suspicious", 0)
            finding.total_analysis = (
                stats.get("harmless", 0)
                + stats.get("malicious", 0)
                + stats.get("suspicious", 0)
                + stats.get("undetected", 0)
            )
            finding.whois = data.get("whois")
            finding.save(
                update_fields=["reputation", "malicious_analysis", "suspicious_analysis", "total_analysis", "whois"]
            )
        except Exception as ex:
            self.logger.error(f"[{self.__class__.__name__}] Error processing host with ID {finding.id}: {str(ex)}")
