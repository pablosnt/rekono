"""Integration with the GitHub Security Advisory database."""

from typing import Any

from framework.platforms import BaseCveProvider


class GHSA(BaseCveProvider):
    """CVE provider that completes the vulnerabilities with the GitHub advisories.

    Attributes:
        url: Endpoint that searches advisories by CVE identifier.
    """

    url = "https://api.github.com/advisories?direction=asc&cve_id={cve}"

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Get the advisories that GitHub has about a CVE.

        Args:
            cve: CVE identifier to search for.

        Returns:
            The advisories that GitHub reports for the CVE, which is an empty list
            if it doesn't know it.
        """
        return self._request(self.session.get, self.url.format(cve=cve))

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> BaseCveProvider.CveEnrichment | None:
        """Get the CVE data that Rekono uses from what GitHub reports.

        Args:
            cve: CVE identifier that was searched for.
            data: Advisories that GitHub reported.

        Returns:
            The data to complete the vulnerability with, or None if GitHub didn't
            report any advisory about the CVE.
        """
        if isinstance(data, dict) or len(data or []) == 0:
            return
        info = data[0]
        cvss_base_score = cvss_vector = cvss_version = None
        # GitHub reports the score of every CVSS version that it knows, so the newest one that
        # actually has a score is the one taken
        for version in ["4", "3", "2"]:
            _cvss = info["cvss_severities"].get(f"cvss_v{version}")
            cvss_base_score = _cvss.get("score", 0)
            if not _cvss or cvss_base_score == 0:
                continue
            cvss_vector = _cvss.get("vector_string")
            cvss_version = f"{version}.0"
            # The vector says which minor version was used to calculate the score, which the
            # key of the score doesn't
            if cvss_vector:
                parsed_version = cvss_vector.replace("CVSS:", "").split("/", 1)[0]
                if parsed_version and parsed_version.startswith(version):
                    cvss_version = parsed_version
            break
        return self.CveEnrichment(
            name=info["summary"],
            description=info["description"],
            cwes=[c["cwe_id"] for c in info.get("cwes") or [] if c.get("cwe_id")],
            cvss_base_score=cvss_base_score,
            cvss_vector=cvss_vector,
            cvss_version=cvss_version,
            epss_score=info.get("epss", {}).get("percentage") * 100 if info.get("epss", {}).get("percentage") else None,
            epss_percentile=info.get("epss", {}).get("percentile") * 100
            if info.get("epss", {}).get("percentile")
            else None,
            technologies=[
                v.get("package", {}).get("name")
                for v in info.get("vulnerabilities", [])
                if v.get("package", {}).get("name")
            ],
            reference=info["html_url"],
            status=info["type"],
            ghsa_id=info["ghsa_id"],
        )

    def cve_quality_score(self, data: BaseCveProvider.CveEnrichment) -> int:
        """Calculate how good the data of a GitHub advisory is.

        Args:
            data: Data that this provider reported about the CVE.

        Returns:
            Zero for the advisories that nobody reviewed, since their data can't
            be trusted over the one of the other providers.
        """
        return 0 if data.status and data.status.lower() == "unreviewed" else super().cve_quality_score(data)
