"""VirusTotal threat intelligence platform integration for host reputation analysis.

Provides the VirusTotal integration class, which enriches Host findings on public IP
addresses or domains with reputation scores, analysis engine detection counts, and
WHOIS data retrieved from the VirusTotal API.
"""

from typing import Any, Callable

from executions.models import Execution
from findings.models import Host
from framework.platforms import BaseIntegration
from platforms.virustotal.models import VirusTotalSettings
from targets.enums import TargetType
from targets.models import Target


class VirusTotal(BaseIntegration):
    """Integration class for VirusTotal threat intelligence platform.

    Extends BaseIntegration to enrich Host findings with reputation scores, analysis
    engine detection counts, and WHOIS data retrieved from the VirusTotal API. Only
    hosts on a public IP are processed, since a host on a private network could carry
    an internal address or hostname that must not be sent to VirusTotal.

    Processing Features:
        - Reputation score and analysis engine detection counts (malicious, suspicious, total)
        - WHOIS data enrichment for domain investigation
        - Availability gated on the configured API key, cached in the database and
          refreshed only when the platform settings are saved

    Attributes:
        finding_types (list): Supported finding types (Host only)
        url (str): VirusTotal API v3 base endpoint URL
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

        Returns the cached availability flag stored on VirusTotalSettings.is_available.
        This flag defaults to False and is only refreshed by
        VirusTotalSettingsSerializer.update, so it reflects the last live check performed
        when the settings were saved through the API, not necessarily the current live
        status. When no API key has ever been configured, the flag stays False and
        process_findings skips this integration without ever calling the VirusTotal API.

        Returns:
            bool: True if the platform was available at the last settings update, False otherwise.
        """
        return self.settings.is_available

    def live_is_available(self) -> bool:
        """Check live connectivity to the VirusTotal API.

        Returns False immediately when no API key is configured, without making any
        request. Otherwise performs a test request for a well-known public IP address
        (Google's public DNS) and returns whether it succeeds.

        Returns:
            bool: True if an API key is configured and the test request succeeds, False otherwise.
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
        """Make an HTTP request to the VirusTotal API with the API key attached.

        Prefixes the given path with the VirusTotal base URL and delegates to
        BaseIntegration._request, adding the "x-apikey" header with the configured secret.

        Args:
            method (Callable): HTTP method to use (GET, POST, etc.)
            url (str): API endpoint path relative to the VirusTotal base URL
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

        Queries the VirusTotal API by domain when the host has one, otherwise by IP
        address, and updates the finding with the reputation score, analysis engine
        detection counts (malicious, suspicious, and total), and WHOIS data from the
        response. Any failure is caught and logged here so it never interrupts the
        processing of the other findings from the same execution.

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
