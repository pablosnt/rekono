"""Open Source Vulnerabilities (OSV) database integration.

Provides integration with the OSV database for automated vulnerability enrichment,
CVSS scoring, and affected package information from the open-source vulnerability
intelligence platform maintained by Google.
"""

from typing import Any

from cvss import CVSS2, CVSS3, CVSS4, CVSSError

from framework.platforms import BaseCveProvider

# Maps OSV severity type strings to their corresponding CVSS parser classes
cvss_class_mapping = {"CVSS_V2": CVSS2, "CVSS_V3": CVSS3, "CVSS_V4": CVSS4}


class OSV(BaseCveProvider):
    """Integration class for the Open Source Vulnerabilities (OSV) database.

    Provides automated vulnerability enrichment by querying the OSV API for CVE
    details, CVSS scores computed from vector strings, and affected package
    identifiers (preferring PURLs over package names) from the OSV platform.

    Attributes:
        url (str): OSV API endpoint URL template for CVE queries.
        reference (str): OSV vulnerability detail page URL template.
    """

    url = "https://api.osv.dev/v1/vulns/{cve}"
    reference = "https://osv.dev/vulnerability/{cve}"

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Retrieve CVE information from the OSV API.

        Args:
            cve (str): CVE identifier to retrieve information for.

        Returns:
            dict[str, Any]: JSON response containing OSV vulnerability details.
        """
        return self._request(self.session.get, self.url.format(cve=cve))

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> BaseCveProvider.CveEnrichment | None:
        """Parse OSV API response into a standardized CVE enrichment object.

        Selects the highest available CVSS version (v4 > v3 > v2) and computes
        the base score by parsing the CVSS vector string using the cvss library.

        Args:
            cve (str): CVE identifier being parsed.
            data (list[dict[str, Any]] | dict[str, Any]): OSV API vulnerability record.

        Returns:
            BaseCveProvider.CveEnrichment | None: Parsed enrichment data, or None if invalid.
        """
        if isinstance(data, list) or not data:
            return
        cvss_base_score = cvss_vector = cvss_version = None
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
                                pass
                        break
                if cvss_vector:
                    break
        technologies = []
        for affected in data.get("affected", []):
            package = affected.get("package", {}).get("purl") or affected.get("package", {}).get("name")
            if affected.get("package") and package:
                technologies.append(package)
            elif affected.get("versions"):
                technologies.extend(affected.get("versions", []))
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
