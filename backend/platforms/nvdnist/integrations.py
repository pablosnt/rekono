"""NVD NIST vulnerability intelligence platform integration.

Provides integration with the National Vulnerability Database (NVD) for
automated vulnerability enrichment, CVSS scoring, and security intelligence
gathering during security assessments.
"""

from typing import Any

from framework.platforms import BaseCveProvider
from platforms.nvdnist.models import NvdNistSettings


class NvdNist(BaseCveProvider):
    """Integration class for NVD NIST vulnerability intelligence platform.

    Provides automated vulnerability enrichment by querying the National
    Vulnerability Database API for detailed CVE information, CVSS scores,
    CWE classifications, and vulnerability descriptions.

    Processing Features:
        - Automated CVE data retrieval and parsing
        - CVSS score mapping to Rekono severity levels
        - CVSS version and vector string extraction
        - CVSS base score preservation for detailed analysis
        - CWE code extraction and classification
        - Vulnerability description and reference updates
        - API token authentication for enhanced rate limits

    Attributes:
        url (str): NVD API endpoint URL template for CVE queries
        reference (str): NVD vulnerability detail page URL template
    """

    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve}"
    reference = "https://nvd.nist.gov/vuln/detail/{cve}"

    @property
    def settings(self) -> NvdNistSettings:
        """Get NVD NIST platform configuration settings from database.

        Returns:
            NvdNistSettings: NVD NIST configuration instance or None if not configured.
        """
        return NvdNistSettings.objects.first()

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Retrieve CVE information from NVD API.

        Makes authenticated or unauthenticated requests to the NVD API
        based on available API token configuration.

        Args:
            cve (str): CVE identifier to retrieve information for

        Returns:
            dict[str, Any]: JSON response containing CVE details and metadata
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
        """Parse NVD API response into a standardized CVE enrichment object.

        Takes the first English description and collects every valid CWE identifier
        reported across all weaknesses. The CVSS base score is read by iterating
        primary then secondary metric categories and CVSS versions from newest to
        oldest, stopping as soon as a base score is found.

        Args:
            cve (str): CVE identifier being parsed.
            data (list[dict[str, Any]] | dict[str, Any]): NVD API response.

        Returns:
            BaseCveProvider.CveEnrichment | None: Parsed enrichment data, or None if not found.
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
        """Extract affected technology CPE identifiers from NVD configuration data.

        Traverses the nested configurations structure to collect all CPE criteria
        strings, which identify the software products and versions affected by
        the vulnerability.

        Args:
            data (dict[str, Any]): NVD API CVE record.

        Returns:
            list[str]: CPE criteria strings collected from all configuration nodes.
        """
        technologies = []
        for configuration in data.get("configurations") or []:
            for node in configuration.get("nodes") or []:
                for cpe in node.get("cpeMatch") or []:
                    if cpe.get("criteria"):
                        technologies.append(cpe.get("criteria"))
        return technologies

    def cve_quality_score(self, data: BaseCveProvider.CveEnrichment) -> int:
        """Calculate NVD-specific data quality score.

        Returns 0 outright for statuses that have not completed NVD's initial analysis or
        were rejected ("received", "awaiting analysis", "undergoing analysis", "deferred",
        "rejected"), since their data is not reliable yet. A CVE still in the "modified"
        status keeps its base score minus a small penalty, since it is being revised again
        after already going through analysis.

        Args:
            data (BaseCveProvider.CveEnrichment): CVE enrichment data to score.

        Returns:
            int: Quality score adjusted for NVD analysis status.
        """
        status = data.status.lower()
        if status in ["received", "rejected", "awaiting analysis", "undergoing analysis", "deferred"]:
            return 0
        score = super().cve_quality_score(data)
        return score - 4 if status == "modified" else score
