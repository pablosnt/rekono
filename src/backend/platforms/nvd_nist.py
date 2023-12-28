from typing import List

from executions.models import Execution
from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration


class NvdNist(BaseIntegration):
    def __init__(self) -> None:
        self.url = "https://services.nvd.nist.gov/rest/json/cve/1.0/{cve}"
        super().__init__()
        self.reference = "https://nvd.nist.gov/vuln/detail/{cve}"
        self.cvss_mapping = {
            Severity.CRITICAL: (9, 11),
            Severity.HIGH: (7, 9),
            Severity.MEDIUM: (4, 7),
            Severity.LOW: (2, 4),
            Severity.INFO: (0, 2),
        }

    def process_findings(self, execution: Execution, findings: List[Finding]) -> None:
        super().process_findings(execution, findings)
        for finding in findings:
            if isinstance(finding, Vulnerability) and finding.cve:
                try:
                    data = self._request(
                        self.session.get, self.url.format(cve=finding.cve)
                    )
                except Exception:
                    continue
                cve_info = data["result"]["CVE_Items"][0]
                for description in (
                    cve_info["cve"]["description"]["description_data"] or []
                ):
                    if description.get("lang") == "en":
                        finding.description = description.get("value")
                        break
                for problem in cve_info["cve"]["problemtype"]["problemtype_data"] or []:
                    for description in problem.get("description") or []:
                        if description.get("value") and description.get(
                            "value"
                        ).lower().startswith("cwe-"):
                            finding.cwe = description.get("value")
                            break
                severity = 5
                for field in ["baseMetricV3", "baseMetricV2"]:
                    if field in cve_info["impact"]:
                        severity = cve_info["impact"][field][
                            f"cvss{field.replace('baseMetric', '')}"
                        ]["baseScore"]
                        break
                finding.severity = [
                    k
                    for k, v in self.cvss_mapping.items()
                    if severity >= v[0] and severity < v[1]
                ][0]
                finding.reference = self.reference.format(cve=finding.cve)
                finding.save(
                    update_fields=["description", "severity", "cwe", "reference"]
                )
