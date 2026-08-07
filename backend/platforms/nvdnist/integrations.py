"""Integration with the National Vulnerability Database of the NIST."""

from typing import Any

from framework.platforms import BaseCveProvider
from platforms.nvdnist.models import NvdNistSettings


class NvdNist(BaseCveProvider):
    """CVE provider that completes the vulnerabilities with the NVD data.

    Attributes:
        url: Endpoint that returns a vulnerability by its CVE identifier.
        reference: Page of a vulnerability, which the findings link to.
    """

    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve}"
    reference = "https://nvd.nist.gov/vuln/detail/{cve}"

    @property
    def settings(self) -> NvdNistSettings:
        """The NVD NIST configuration, or None if it hasn't been created yet."""
        return NvdNistSettings.objects.first()

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Get the data that NVD has about a CVE.

        Args:
            cve: CVE identifier to search for.

        Returns:
            The vulnerability that NVD reports, or an empty list if it doesn't
            know the CVE.
        """
        if self.settings.secret is None:
            response = self._request(self.session.get, self.url.format(cve=cve))
        response = self._request(self.session.get, self.url.format(cve=cve), headers={"apiKey": self.settings.secret})
        return (
            response.get("vulnerabilities", [])[0].get("cve", {})
            if len(response.get("vulnerabilities", []) or []) > 0
            else response.get("vulnerabilities", [])
        )

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> BaseCveProvider.CveEnrichment | None:
        """Get the CVE data that Rekono uses from what NVD reports.

        Args:
            cve: CVE identifier that was searched for.
            data: Vulnerability that NVD reported.

        Returns:
            The data to complete the vulnerability with, or None if NVD didn't
            report anything about the CVE.
        """
        if isinstance(data, list):
            return
        enrichment = self.CveEnrichment(
            name=data.get("cisaVulnerabilityName", cve) or cve,
            cwes=[],
            technologies=self._get_technologies(data),
            reference=self.reference.format(cve=cve),
            status=data.get("vulnStatus", ""),
        )
        for desc in data.get("descriptions") or []:
            if desc.get("lang") == "en":
                enrichment.description = desc.get("value")
                break
        for weakness in data.get("weaknesses", []) or []:
            for description in weakness.get("description") or []:
                value = description.get("value", "").lower()
                if value.startswith("cwe-") and value != "cwe-0":
                    enrichment.cwes.append(value.upper())

        # NVD reports the score that itself calculated apart from the ones that other
        # organizations calculated, and the newest CVSS version is the most accurate one, so
        # the scores are walked from the most reliable one to the least one
        cvss_info = data.get("metrics", {}) or {}
        for category in ["primary", "secondary"]:
            if enrichment.cvss_base_score:
                break
            for _version in ["40", "4", "31", "30", "3", "2"]:
                cvss_version_field = f"cvssMetricV{_version}"
                for cvss in cvss_info.get(cvss_version_field) or sum(
                    [list(items) for key, items in cvss_info.items() if key.lower().startswith(cvss_version_field)],
                    [],
                ):
                    if cvss.get("type", "").lower() == category:
                        cvss_info = cvss.get("cvssData", {})
                        base_score = cvss_info.get("baseScore")
                        if base_score:
                            enrichment.cvss_version = cvss_info.get("version")
                            enrichment.cvss_vector = cvss_info.get("vectorString")
                            enrichment.cvss_base_score = base_score
                            break
        return enrichment

    def _get_technologies(self, data: dict[str, Any]) -> list[str]:
        """Get the technologies that a vulnerability affects, as CPE identifiers.

        Args:
            data: Vulnerability that NVD reported.

        Returns:
            Every CPE of the configurations that NVD reports as vulnerable.
        """
        technologies = []
        for configuration in data.get("configurations") or []:
            for node in configuration.get("nodes") or []:
                for cpe in node.get("cpeMatch") or []:
                    if cpe.get("criteria"):
                        technologies.append(cpe.get("criteria"))
        return technologies

    def cve_quality_score(self, data: BaseCveProvider.CveEnrichment) -> int:
        """Calculate how good the data that NVD reported about a CVE is.

        Args:
            data: Data that this provider reported about the CVE.

        Returns:
            Zero for the CVEs that NVD hasn't analyzed yet or that it rejected,
            since their data isn't reliable, and a penalized score for the ones
            that are being revised again after having been analyzed.
        """
        status = data.status.lower()
        if status in ["received", "rejected", "awaiting analysis", "undergoing analysis", "deferred"]:
            return 0
        score = super().cve_quality_score(data)
        return score - 4 if status == "modified" else score
