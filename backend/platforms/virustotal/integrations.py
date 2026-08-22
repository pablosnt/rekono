"""Integration with the VirusTotal threat intelligence platform."""

from typing import Any, Callable

from executions.models import Execution
from findings.models import Host
from framework.platforms import BaseIntegration
from platforms.virustotal.models import VirusTotalSettings
from targets.enums import TargetType
from targets.models import Target


class VirusTotal(BaseIntegration):
    """Integration that says how dangerous a host is and who owns its address.

    Attributes:
        finding_types: Only the hosts have a reputation.
        url: Base URL of the API.
    """

    finding_types = [Host]
    url = "https://www.virustotal.com/api/v3/"

    @property
    def settings(self) -> VirusTotalSettings:
        """The VirusTotal configuration, or None if it hasn't been created yet."""
        return VirusTotalSettings.objects.first()

    def is_available(self) -> bool:
        """Check if the platform can be used.

        Returns:
            Whether the platform answered the last time that the API token was
            saved, since checking it on every finding would waste the requests
            that the token allows.
        """
        return self.settings.is_available

    def live_is_available(self) -> bool:
        """Check if the platform answers right now.

        Returns:
            Whether an API token is configured and VirusTotal answers about a host
            that it's known to have, so a platform that answers something else
            isn't used.
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
        """Make a request to the VirusTotal API.

        Args:
            method: Method of the session that sends the request.
            url: Path of the endpoint, without the base URL of the API.
            json: Whether the response must be parsed as JSON.
            trigger_exception: Whether a failed request must raise an exception.
            **kwargs: Extra arguments for the request, like its parameters.

        Returns:
            The response of the platform, with the API token already included in
            the request.
        """
        return super()._request(
            method,
            f"{self.url}{url}",
            json,
            trigger_exception,
            **{**kwargs, "headers": {"accept": "application/json", "x-apikey": self.settings.secret}},
        )

    def is_finding_processable(self, finding: Host) -> bool:
        """Check if this platform can say anything about a finding.

        Args:
            finding: Finding whose type and data are checked.

        Returns:
            Whether the host has a public IP address, since nothing about a host
            of a private network can be sent to VirusTotal.
        """
        # The IP type is the only gate: never send anything (IP or domain) for a host on a private
        # network, since its domain would be an internal hostname that we must not leak to VirusTotal
        return super().is_finding_processable(finding) and Target.get_type(finding.ip) is TargetType.PUBLIC_IP

    def _process_finding(self, execution: Execution, finding: Host) -> None:
        """Complete a discovered host with its reputation and its WHOIS record.

        Args:
            execution: Execution that discovered the host.
            finding: Host to complete.
        """
        try:
            # The domain is more specific than the IP address, since several domains can
            # resolve to the same address
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
