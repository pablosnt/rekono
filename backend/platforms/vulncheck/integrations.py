"""Integration with the NVD++ service of VulnCheck."""

from typing import Any

from platforms.nvdnist.integrations import NvdNist
from platforms.vulncheck.models import VulnCheckSettings


class VulnCheck(NvdNist):
    """CVE provider that completes the vulnerabilities with the NVD++ data.

    NVD++ reports the vulnerabilities in the same format as NVD, so only how they
    are requested and how their technologies are read differ from it.

    Attributes:
        url: Endpoint that returns a vulnerability by its CVE identifier.
    """

    url = "https://api.vulncheck.com/v3/index/nist-nvd2"

    @property
    def settings(self) -> VulnCheckSettings:
        """The VulnCheck configuration, or None if it hasn't been created yet."""
        return VulnCheckSettings.objects.first()

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Get the data that VulnCheck has about a CVE.

        Args:
            cve: CVE identifier to search for.

        Returns:
            The vulnerability that VulnCheck reports, or an empty dict if it
            doesn't know the CVE.
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
        """Get the technologies that a vulnerability affects, as CPE identifiers.

        Args:
            data: Vulnerability that VulnCheck reported.

        Returns:
            The CPEs that VulnCheck already resolved, which are the exact versions
            that the version ranges of NVD cover, or the NVD ones if VulnCheck
            didn't resolve them.
        """
        vc_cpes = data.get("vcVulnerableCPEs")
        if vc_cpes:
            return vc_cpes
        return super()._get_technologies(data)

    def is_available(self) -> bool:
        """Check if the platform can be used.

        Returns:
            Whether an API token is configured and the platform answers with it,
            since VulnCheck rejects the requests that aren't authenticated.
        """
        if not self.settings or not self.settings.secret:
            return False
        return super().is_available()
