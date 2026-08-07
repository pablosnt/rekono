"""Integration with the Exploit Prediction Scoring System of FIRST."""

import re

from executions.models import Execution
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration
from security.validators.enums import Regex


class First(BaseIntegration):
    """Integration that says how likely a vulnerability is to be exploited.

    The probability changes over time, so it isn't only calculated when a
    vulnerability is discovered, it's also refreshed by the monitor job.

    Attributes:
        finding_types: Only the vulnerabilities have an exploitation probability.
        url: Endpoint that returns the probability of a group of CVEs.
    """

    finding_types = [Vulnerability]
    url = "https://api.first.org/data/v1/epss"

    def is_finding_processable(self, finding: Finding) -> bool:
        """Check if this platform can say anything about a finding.

        Args:
            finding: Finding whose type and data are checked.

        Returns:
            Whether the finding is a vulnerability with a known CVE, since the
            probability is calculated per CVE.
        """
        return super().is_finding_processable(finding) and finding.cve is not None

    def is_available(self) -> bool:
        """Check if the platform can be used.

        Returns:
            Whether the API answers with the probability of a CVE that it's known
            to have, so a platform that answers something else isn't used.
        """
        try:
            return bool(self._get_epss_for_cves(["CVE-2022-27225"]))
        except Exception:
            return False

    def _get_epss_for_cves(self, cves: list[str]) -> list[dict[str, str]]:
        """Get the exploitation probability of a group of CVEs.

        Args:
            cves: CVE identifiers to ask about.

        Returns:
            The probability of each CVE and its position among all the scored
            ones, without the CVEs that FIRST doesn't know.
        """
        return self._request(self.session.get, self.url, params={"cve": ",".join(cves)}).get("data", [])

    def _process_finding(self, execution: Execution, finding: Vulnerability) -> None:
        """Save the exploitation probability of a discovered vulnerability.

        Args:
            execution: Execution that discovered the vulnerability.
            finding: Vulnerability to complete with its probability.
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
        """Refresh the exploitation probability of the vulnerabilities still open.

        The CVEs are asked for in batches, and a batch that fails is logged and
        skipped, so the rest of the vulnerabilities are still refreshed.
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
