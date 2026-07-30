"""FIRST EPSS integration for exploit prediction scoring.

Provides integration with the FIRST Exploit Prediction Scoring System (EPSS) API
for automated enrichment of vulnerability findings with exploit probability scores
and percentile rankings updated on a per-execution and bulk monitoring basis.
"""

import re

from executions.models import Execution
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration
from security.validators.enums import Regex


class First(BaseIntegration):
    """Integration class for the FIRST Exploit Prediction Scoring System (EPSS).

    Enriches vulnerability findings with EPSS scores and percentile rankings
    from the FIRST API. Supports both per-execution enrichment for individual
    CVEs and bulk monitoring to keep EPSS data current across all active findings.

    Processing Features:
        - Per-execution EPSS enrichment for a single vulnerability finding
        - Bulk EPSS monitoring across all non-fixed vulnerabilities, in batches of 100 CVEs
        - CVE identifier validation before bulk requests to keep malformed values out of a batch

    Attributes:
        finding_types (list): Supported finding types (Vulnerability only).
        url (str): FIRST EPSS API endpoint URL.
    """

    finding_types = [Vulnerability]
    url = "https://api.first.org/data/v1/epss"

    def is_finding_processable(self, finding: Finding) -> bool:
        """Check if a finding can be enriched with EPSS data.

        Args:
            finding (Finding): The finding to evaluate.

        Returns:
            bool: True if the finding is a vulnerability with a CVE identifier.
        """
        return super().is_finding_processable(finding) and finding.cve is not None

    def is_available(self) -> bool:
        """Check if the FIRST EPSS API is reachable and returning data.

        Validates platform connectivity by performing a live API request for a
        known CVE. Returns True if the API responds with at least one EPSS record.

        Returns:
            bool: True if the FIRST EPSS API is reachable and returns data, False otherwise.
        """
        try:
            return bool(self._get_epss_for_cves(["CVE-2022-27225"]))
        except Exception:
            return False

    def _get_epss_for_cves(self, cves: list[str]) -> list[dict[str, str]]:
        """Retrieve EPSS scores for a batch of CVEs from the FIRST API.

        Args:
            cves (list[str]): CVE identifiers to retrieve EPSS data for.

        Returns:
            list[dict[str, str]]: List of EPSS records, each containing cve, epss,
                percentile, and date fields.
        """
        return self._request(self.session.get, self.url, params={"cve": ",".join(cves)}).get("data", [])

    def _process_finding(self, execution: Execution, finding: Vulnerability) -> None:
        """Enrich a single vulnerability finding with its current EPSS score.

        Queries the FIRST EPSS API for the finding's CVE and updates the
        epss_score and epss_percentile fields if data is available.

        Args:
            execution (Execution): The execution that produced the finding.
            finding (Vulnerability): The vulnerability to enrich with EPSS data.
        """
        data = self._get_epss_for_cves([finding.cve])
        if len(data) == 1 and data[0]["cve"] == finding.cve:
            update_fields = []
            if data[0]["epss"]:
                finding.epss_score = float(data[0]["epss"]) * 100
                update_fields.append("epss_score")
            if data[0]["percentile"]:
                finding.epss_percentile = float(data[0]["percentile"]) * 100
                update_fields.append("epss_percentile")
            if len(update_fields) > 0:
                finding.save(update_fields=update_fields)

    def monitor(self) -> None:
        """Bulk-update EPSS scores for all active vulnerability findings.

        Retrieves the latest EPSS data in batches of 100 CVEs from the FIRST API and
        updates epss_score and epss_percentile across all non-fixed vulnerabilities
        with a CVE identifier. Failures on individual batches are silently skipped.
        """
        if not self.is_enabled():
            return
        # Keep only well-formed CVE identifiers. A single blank or malformed value inside a batch
        # can make the FIRST API reject the whole request, and the except below would then drop all
        # 100 CVEs in that batch. Filtering up front isolates bad data from valid CVEs.
        cves = [
            cve
            for cve in Vulnerability.objects.filter(cve__isnull=False, is_fixed=False)
            .values_list("cve", flat=True)
            .distinct()
            if cve and re.fullmatch(Regex.CVE.value, cve)
        ]
        for i in range(0, len(cves), 100):
            try:
                data = self._get_epss_for_cves(cves[i : i + 100])
                for item in data:
                    data_to_update = {
                        k: v
                        for k, v in {
                            "epss_score": float(item["epss"]) * 100 if item["epss"] else None,
                            "epss_percentile": float(item["percentile"]) * 100 if item["percentile"] else None,
                        }.items()
                        if v is not None
                    }
                    if data_to_update:
                        Vulnerability.objects.filter(cve=item["cve"], is_fixed=False).update(**data_to_update)
            except Exception as ex:
                self.logger.error(
                    f"[{self.__class__.__name__}] Error getting EPSS score and percentile for CVEs: {str(ex)}"
                )
