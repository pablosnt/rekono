"""ENISA European Vulnerability Database (EUVD) integration.

Provides integration with the ENISA EUVD for automated vulnerability enrichment,
CVSS scoring, EPSS data, and affected product information gathered from the
European vulnerability intelligence platform.
"""

from typing import Any

from framework.platforms import BaseCveProvider


class EUVD(BaseCveProvider):
    """Integration class for the ENISA European Vulnerability Database.

    Provides automated vulnerability enrichment by querying the EUVD API
    for CVE details, CVSS scores, EPSS probability scores, and affected
    product identifiers from the ENISA vulnerability intelligence platform.

    Attributes:
        url (str): EUVD search API endpoint URL template for CVE queries.
        reference (str): EUVD vulnerability detail page URL template.
    """

    url = "https://euvdservices.enisa.europa.eu/api/search?text={cve}"
    reference = "https://euvd.enisa.europa.eu/vulnerability/{euvd}"

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Retrieve CVE information from the EUVD API.

        Searches the EUVD by CVE identifier and returns the matching entry
        by comparing the CVE against the aliases field of each result.

        Args:
            cve (str): CVE identifier to retrieve information for.

        Returns:
            dict[str, Any]: Matching EUVD vulnerability record, or empty dict if not found.
        """
        response = self._request(self.session.get, self.url.format(cve=cve))
        for item in response.get("items") or []:
            if cve in item.get("aliases", "").split("\n"):
                return item
        return {}

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> BaseCveProvider.CveEnrichment | None:
        """Parse EUVD API response into a standardized CVE enrichment object.

        Args:
            cve (str): CVE identifier being parsed.
            data (list[dict[str, Any]] | dict[str, Any]): EUVD vulnerability record.

        Returns:
            BaseCveProvider.CveEnrichment | None: Parsed enrichment data, or None if invalid.
        """
        if isinstance(data, list) or not data:
            return
        return self.CveEnrichment(
            name=data["id"],
            description=data["description"],
            cvss_base_score=data.get("baseScore"),
            cvss_vector=data.get("baseScoreVector"),
            cvss_version=data.get("baseScoreVersion"),
            epss_score=data.get("epss"),
            technologies=[p.get("id") for p in data.get("enisaIdProduct", []) if p.get("id")],
            reference=self.reference.format(euvd=data["id"]),
            euvd_id=data["id"],
        )
