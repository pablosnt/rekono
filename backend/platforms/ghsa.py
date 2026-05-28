"""GitHub Security Advisory (GHSA) database integration.

Provides integration with the GitHub Security Advisory database for automated
vulnerability enrichment, CVSS scoring, CWE classification, EPSS data, and
affected package information gathered from the GitHub advisory platform.
"""

from typing import Any

from framework.platforms import BaseCveProvider


class GHSA(BaseCveProvider):
    """Integration class for the GitHub Security Advisory database.

    Provides automated vulnerability enrichment by querying the GitHub Advisory
    API for CVE details, CVSS scores, CWE identifiers, EPSS probability data,
    and affected package names from the GitHub security advisory platform.

    Attributes:
        url (str): GitHub Advisory API endpoint URL template for CVE queries.
    """

    url = "https://api.github.com/advisories?direction=asc&cve_id={cve}"

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Retrieve CVE information from the GitHub Advisory API.

        Args:
            cve (str): CVE identifier to retrieve information for.

        Returns:
            dict[str, Any]: List of matching GitHub advisory records.
        """
        return self._request(self.session.get, self.url.format(cve=cve))

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> BaseCveProvider.CveEnrichment | None:
        """Parse GitHub Advisory API response into a standardized CVE enrichment object.

        Selects the highest available CVSS version (v4 > v3 > v2) and extracts
        the CVSS version string from the vector. Unreviewed advisories are handled
        by cve_quality_score returning 0 to deprioritize them.

        Args:
            cve (str): CVE identifier being parsed.
            data (list[dict[str, Any]] | dict[str, Any]): GitHub advisory API response.

        Returns:
            BaseCveProvider.CveEnrichment | None: Parsed enrichment data, or None if invalid.
        """
        if isinstance(data, dict) or len(data or []) == 0:
            return
        info = data[0]
        cvss_data = {}
        for key in ["4", "3", "2"]:
            _cvss = info["cvss_severities"].get(f"cvss_v{key}")
            if not _cvss or _cvss.get("score", 0) == 0:
                continue
            cvss_data = _cvss
            break
        return self.CveEnrichment(
            name=info["summary"],
            description=info["description"],
            cwe=info["cwes"][-1]["cwe_id"] if len(info.get("cwes") or []) else None,
            cvss_base_score=cvss_data.get("score"),
            cvss_vector=cvss_data.get("vector_string"),
            cvss_version=cvss_data.get("vector_string", "").replace("CVSS:", "").split("/", 1)[0]
            if cvss_data.get("vector_string")
            else None,
            epss_score=info.get("epss", {}).get("percentage"),
            epss_percentile=info.get("epss", {}).get("percentile"),
            technologies=[
                v.get("package", {}).get("name")
                for v in info.get("vulnerabilities", [])
                if v.get("package", {}).get("name")
            ],
            reference=info["html_url"],
            status=info["type"],
        )

    def cve_quality_score(self, data: BaseCveProvider.CveEnrichment) -> int:
        """Calculate data quality score, returning 0 for unreviewed advisories.

        Unreviewed GitHub advisories have lower reliability, so they are assigned
        a score of 0 to prevent them from overriding higher-quality provider data.

        Args:
            data (BaseCveProvider.CveEnrichment): CVE enrichment data to score.

        Returns:
            int: 0 for unreviewed advisories, or the standard quality score otherwise.
        """
        return 0 if data.status and data.status.lower() == "unreviewed" else super().cve_quality_score(data)
