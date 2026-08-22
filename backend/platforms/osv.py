"""Integration with the Open Source Vulnerabilities database."""

from typing import Any

from cvss import CVSS2, CVSS3, CVSS4, CVSSError

from framework.platforms import BaseCveProvider

# Class that calculates the score of a vector, for each CVSS version that OSV can report
cvss_class_mapping = {"CVSS_V2": CVSS2, "CVSS_V3": CVSS3, "CVSS_V4": CVSS4}


class OSV(BaseCveProvider):
    """CVE provider that completes the vulnerabilities with the OSV data.

    Attributes:
        url: Endpoint that returns a vulnerability by its identifier.
        reference: Page of a vulnerability, which the findings link to.
    """

    url = "https://api.osv.dev/v1/vulns/{cve}"
    reference = "https://osv.dev/vulnerability/{cve}"

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Get the data that OSV has about a CVE.

        Args:
            cve: CVE identifier to search for.

        Returns:
            The vulnerability that OSV reports, or an empty dict if it doesn't
            know the CVE.
        """
        return self._request(self.session.get, self.url.format(cve=cve))

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> BaseCveProvider.CveEnrichment | None:
        """Get the CVE data that Rekono uses from what OSV reports.

        Args:
            cve: CVE identifier that was searched for.
            data: Vulnerability that OSV reported.

        Returns:
            The data to complete the vulnerability with, or None if OSV didn't
            report anything about the CVE. The score is calculated from the CVSS
            vector, since OSV only reports the vector itself.
        """
        if isinstance(data, list) or not data:
            return
        cvss_base_score = cvss_vector = cvss_version = None
        # OSV reports the vector of every CVSS version that it knows, so the newest one is the
        # one taken
        if data.get("severity"):
            for version in ["4", "3", "2"]:
                for severity in data.get("severity") or []:
                    if severity["type"] == f"CVSS_V{version}":
                        cvss_vector = severity.get("score")
                        cvss_version = f"{version}.0"
                        if cvss_vector:
                            parsed_version = cvss_vector.replace("CVSS:", "").split("/", 1)[0]
                            if parsed_version and parsed_version.startswith(version):
                                cvss_version = parsed_version
                        if cvss_vector and severity.get("type") in cvss_class_mapping:
                            try:
                                cvss_base_score = float(cvss_class_mapping[severity["type"]](cvss_vector).scores()[0])
                            except CVSSError:
                                # A malformed vector string is skipped, leaving cvss_base_score unset
                                pass
                        break
                if cvss_vector:
                    break
        # The PURL identifies a package better than its name, but not every ecosystem provides
        # one, and some entries only say which versions are affected
        technologies = []
        for affected in data.get("affected", []):
            package = affected.get("package", {}).get("purl") or affected.get("package", {}).get("name")
            if affected.get("package") and package:
                technologies.append(package)
            elif affected.get("versions"):
                technologies.extend(affected.get("versions", []))
        # OSV lists all the identifiers that a vulnerability has, so the ones that Rekono
        # stores apart are taken from there, and the rest is kept as the OSV identifier
        euvd_id = ghsa_id = osv_generic_id = None
        for alias in data.get("aliases") or []:
            alias_upper = alias.upper()
            if alias_upper.startswith("GHSA-") and ghsa_id is None:
                ghsa_id = alias
            elif alias_upper.startswith("EUVD-") and euvd_id is None:
                euvd_id = alias
            elif (
                not alias_upper.startswith("CVE-")
                and not alias_upper.startswith("GHSA-")
                and not alias_upper.startswith("EUVD-")
                and osv_generic_id is None
            ):
                osv_generic_id = alias
            if euvd_id and ghsa_id and osv_generic_id:
                break
        return self.CveEnrichment(
            name=data.get("summary", data["id"]),
            description=data.get("details"),
            cvss_base_score=cvss_base_score,
            cvss_vector=cvss_vector,
            cvss_version=cvss_version,
            technologies=technologies,
            reference=self.reference.format(cve=cve),
            euvd_id=euvd_id,
            ghsa_id=ghsa_id,
            osv_generic_id=osv_generic_id,
        )
