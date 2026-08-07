"""Integration with the European Vulnerability Database of ENISA."""

from typing import Any

from framework.platforms import BaseCveProvider


class EUVD(BaseCveProvider):
    """CVE provider that completes the vulnerabilities with the EUVD data.

    Attributes:
        url: Endpoint that searches vulnerabilities by their identifier.
        reference: Page of a vulnerability, which the findings link to.
    """

    url = "https://euvdservices.enisa.europa.eu/api/search?text={cve}"
    reference = "https://euvd.enisa.europa.eu/vulnerability/{euvd}"

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Get the data that EUVD has about a CVE.

        Args:
            cve: CVE identifier to search for.

        Returns:
            The vulnerability whose aliases include the CVE, or an empty dict if
            EUVD doesn't know it, since the search returns everything that matches
            the text instead of only the requested CVE.
        """
        response = self._request(self.session.get, self.url.format(cve=cve))
        for item in response.get("items") or []:
            if cve in item.get("aliases", "").split("\n"):
                return item
        return {}

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> BaseCveProvider.CveEnrichment | None:
        """Get the CVE data that Rekono uses from what EUVD reports.

        Args:
            cve: CVE identifier that was searched for.
            data: Vulnerability that EUVD reported.

        Returns:
            The data to complete the vulnerability with, or None if EUVD didn't
            report anything about the CVE.
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
