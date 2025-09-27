"""VirusTotal threat intelligence platform integration for host reputation analysis.

This module provides the core integration class for the VirusTotal threat intelligence
platform, enabling real-time reputation analysis, malware detection, and threat
assessment for discovered hosts and domains. The integration automatically processes
Host findings to enrich them with comprehensive threat intelligence data.
"""

from functools import cached_property
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

    @cached_property
    def settings(self) -> VirusTotalSettings:
        """Get VirusTotal platform configuration settings from database.

        Returns:
            VirusTotalSettings: Platform configuration instance or None if not configured.
        """
        return VirusTotalSettings.objects.first()

    def is_available(self) -> bool:
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

    def _request(self, method: Callable, url: str, json: bool = True, trigger_exception: bool = True, **kwargs: Any):
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

        Evaluates whether a Host finding meets the criteria for VirusTotal
        threat intelligence processing based on domain availability or
        public IP address classification.

        Args:
            finding (Host): The Host finding to evaluate for processing

        Returns:
            bool: True if the finding should be processed, False otherwise
        """
        return super().is_finding_processable(finding) and (
            finding.domain is not None or Target.get_type(finding.ip) is TargetType.PUBLIC_IP
        )

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
            elif finding.ip is not None:
                data = self._request(self.session.get, f"ip_addresses/{finding.ip}")
            else:
                return
            data = data.get("data", {}).get("attributes", {})
            finding.reputation = data.get("reputation")
            finding.harmless_votes = data.get("total_votes", {}).get("harmless")
            finding.malicious_votes = data.get("total_votes", {}).get("malicious")
            finding.whois = data.get("whois")
            finding.save(update_fields=["reputation", "harmless_votes", "malicious_votes", "whois"])
        except Exception:
            pass
