"""VulnCheck NVD++ vulnerability intelligence platform integration.

Provides integration with VulnCheck's NVD++ service for automated vulnerability
enrichment. Extends NvdNist to reuse its parsing logic, since VulnCheck mirrors
the NVD response schema exactly. Bearer token authentication is required for
all API requests.
"""

from typing import Any

from platforms.nvdnist.integrations import NvdNist
from platforms.vulncheck.models import VulnCheckSettings


class VulnCheck(NvdNist):
    """Integration class for VulnCheck NVD++ vulnerability intelligence platform.

    Extends NvdNist to query VulnCheck's NVD++ index, which mirrors the NVD schema
    and additionally provides pre-resolved CPE data via vcVulnerableCPEs. Since the
    response schema is otherwise identical to NVD NIST, the parent's _parse_cve
    method is reused directly. The only structural difference is that VulnCheck
    wraps CVE records in a top-level 'data' list rather than 'vulnerabilities',
    which is handled in _get_cve before handing off to the inherited parser.

    Processing Features:
        - CVE data retrieval via VulnCheck NVD++ API with Bearer token authentication
        - CVSS and CWE extraction via inherited NVD NIST parsing logic
        - Technology CPE extraction from vcVulnerableCPEs (pre-resolved specific versions)
        - Required token validation before any API calls are attempted
        - Quality scoring inherited from NvdNist (status-based penalties)

    Attributes:
        url (str): VulnCheck NVD++ API endpoint URL
    """

    url = "https://api.vulncheck.com/v3/index/nist-nvd2"

    @property
    def settings(self) -> VulnCheckSettings:
        """Get VulnCheck platform configuration settings from database.

        Returns:
            VulnCheckSettings: VulnCheck configuration instance or None if not configured.
        """
        return VulnCheckSettings.objects.first()

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Retrieve CVE information from VulnCheck NVD++ API.

        Makes an authenticated request to the VulnCheck NVD++ index using a Bearer
        token. The response wraps CVE records in a top-level 'data' list; this method
        returns the first element directly so the inherited _parse_cve can process it
        without modification.

        Args:
            cve (str): CVE identifier to retrieve information for.

        Returns:
            dict[str, Any]: First CVE record from the response matching the NVD schema,
                            or an empty list if no records were returned.
        """
        response = self._request(
            self.session.get,
            self.url,
            headers={"Authorization": f"Bearer {self.settings.secret}"},
            params={"cve": cve},
        )
        data = response.get("data") or []
        return data[0] if len(data) > 0 else {}

    def _get_technologies(self, data: dict[str, Any]) -> list[str]:
        """Extract affected technology CPE identifiers from VulnCheck response data.

        Uses the pre-resolved vcVulnerableCPEs list when available, which VulnCheck
        provides as a flat list of specific CPE strings already expanded from the
        version ranges in the standard NVD configurations field. Falls back to the
        parent's configurations-based extraction when the field is absent.

        Args:
            data (dict[str, Any]): VulnCheck NVD++ API CVE record.

        Returns:
            list[str]: Specific CPE strings from vcVulnerableCPEs, or CPE criteria
                       strings from NVD configurations as a fallback.
        """
        vc_cpes = data.get("vcVulnerableCPEs")
        if vc_cpes:
            return vc_cpes
        return super()._get_technologies(data)

    def is_available(self) -> bool:
        """Check whether the VulnCheck NVD++ integration is configured and reachable.

        Validates that a Bearer token is configured before attempting any network
        request, since the VulnCheck API requires authentication for all calls.
        Delegates the actual connectivity check to the parent's is_available.

        Returns:
            bool: True if a token is configured and the API returns a valid response,
                  False otherwise.
        """
        if not self.settings or not self.settings.secret:
            return False
        return super().is_available()
