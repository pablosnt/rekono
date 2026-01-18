"""NVD NIST vulnerability intelligence platform integration.

Provides integration with the National Vulnerability Database (NVD) for
automated vulnerability enrichment, CVSS scoring, and security intelligence
gathering during security assessments.
"""

from typing import Any

from executions.models import Execution
from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration
from platforms.nvdnist.models import NvdNistSettings


class NvdNist(BaseIntegration):
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
        finding_types (list): List of finding types processed by this integration
        url (str): NVD API endpoint URL template for CVE queries
        reference (str): NVD vulnerability detail page URL template
        cvss_mapping (dict): CVSS score ranges mapped to Rekono severity levels
    """

    finding_types = [Vulnerability]
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve}"
    reference = "https://nvd.nist.gov/vuln/detail/{cve}"
    cvss_mapping = {
        Severity.CRITICAL: (9, 11),
        Severity.HIGH: (7, 9),
        Severity.MEDIUM: (4, 7),
        Severity.LOW: (2, 4),
        Severity.INFO: (0, 2),
    }

    @property
    def settings(self) -> NvdNistSettings:
        """Get NVD NIST platform configuration settings from database.

        Returns:
            NvdNistSettings: NVD NIST configuration instance or None if not configured.
        """
        return NvdNistSettings.objects.first()

    def is_available(self) -> bool:
        """Check if NVD API token is configured and functional.

        Tests the API token by making a request to retrieve information
        for a known CVE (Log4Shell) to validate authentication and connectivity.

        Returns:
            bool: True if API token is valid and functional, False otherwise
        """
        try:
            # Test the API token by getting Log4Shell information
            self._get_cve("CVE-2021-44228")
            return True
        except Exception:
            return False

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
            return self._request(self.session.get, self.url.format(cve=cve))
        return self._request(self.session.get, self.url.format(cve=cve), headers={"apiKey": self.settings.secret})

    def _process_finding(self, execution: Execution, finding: Vulnerability) -> None:
        """Process and enrich vulnerability finding with NVD data.

        Retrieves detailed vulnerability information from NVD API and updates
        the finding with enhanced data including descriptions, CVSS scores,
        CVSS vector strings, CVSS versions, severity mappings, CWE classifications,
        and official references.

        Args:
            execution (Execution): The execution context for this processing
            finding (Vulnerability): The vulnerability finding to enrich
        """
        try:
            data = self._get_cve(finding.cve)
        except Exception:
            return
        if len(data.get("vulnerabilities", []) or []) == 0:
            return
        update = ["reference"]
        cve_info = data.get("vulnerabilities", [])[0].get("cve", {})
        # Get CVE description
        for description in cve_info.get("descriptions", []) or []:
            if description.get("lang") == "en":
                finding.description = description.get("value")
                update.append("description")
                break
        cwe = severity = 0
        cvss_metrics = cve_info.get("metrics", {}) or {}
        for type in ["primary", "secondary"]:
            if cwe == 0:
                # Get CWE code
                for weakness in cve_info.get("weaknesses", []) or []:
                    if weakness.get("type").lower() != type:
                        continue
                    for description in weakness.get("description") or []:
                        value = description.get("value", "").lower()
                        if value.startswith("cwe-"):
                            cwe_value = int(value.split("cwe-")[1])
                            cwe = cwe_value if cwe_value > cwe else cwe
                    if cwe > 0:
                        finding.cwe = f"CWE-{cwe}"
                        update.append("cwe")
                        break
            if severity == 0:
                for cvss_version_field in [
                    "cvssMetricV40",
                    "cvssMetricV4",
                    "cvssMetricV31",
                    "cvssMetricV30",
                    "cvssMetricV3",
                    "cvssMetricV2",
                ]:
                    for cvss in cvss_metrics.get(cvss_version_field) or sum(
                        [
                            list(items)
                            for key, items in cvss_metrics.items()
                            if key.lower().startswith(cvss_version_field)
                        ],
                        [],
                    ):
                        if cvss.get("type", "").lower() == type:
                            cvss_data = cvss.get("cvssData", {})
                            base_score = cvss_data.get("baseScore")
                            if base_score:
                                severity = base_score
                                finding.severity = [
                                    k for k, v in self.cvss_mapping.items() if base_score >= v[0] and base_score < v[1]
                                ][0]
                                finding.cvss_version = cvss_data.get("version")
                                finding.cvss_vector = cvss_data.get("vectorString")
                                finding.cvss_base_score = base_score
                                update.extend(["severity", "cvss_version", "cvss_vector", "cvss_base_score"])
                                break
                    if severity > 0:
                        break
        finding.reference = self.reference.format(cve=finding.cve)
        finding.save(update_fields=update)

    def is_finding_processable(self, finding: Finding) -> bool:
        """Determine if a finding can be processed by this integration.

        Validates that the finding is a processable vulnerability type
        with a valid CVE identifier for NVD API queries.

        Args:
            finding (Finding): The finding to evaluate for processing

        Returns:
            bool: True if finding has CVE and can be processed, False otherwise
        """
        return super().is_finding_processable(finding) and finding.cve is not None
