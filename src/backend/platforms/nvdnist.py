from executions.models import Execution
from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration


class NvdNist(BaseIntegration):
    def __init__(self) -> None:
        self.url = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve}"
        super().__init__()
        self.reference = "https://nvd.nist.gov/vuln/detail/{cve}"
        self.cvss_mapping = {
            Severity.CRITICAL: (9, 11),
            Severity.HIGH: (7, 9),
            Severity.MEDIUM: (4, 7),
            Severity.LOW: (2, 4),
            Severity.INFO: (0, 2),
        }

    def _process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        for finding in findings:
            if isinstance(finding, Vulnerability) and finding.cve:
                try:
                    data = self._request(
                        self.session.get, self.url.format(cve=finding.cve)
                    )
                except Exception:  # nosec
                    continue
                if len(data.get("vulnerabilities", []) or []) == 0:
                    continue
                cve_info = data.get("vulnerabilities")[0].get("cve", {})
                for description in cve_info.get("descriptions", []) or []:
                    if description.get("lang") == "en":
                        finding.description = description.get("value")
                        break
                cwe_assigned = False
                for weakness in cve_info.get("weaknesses", []) or []:
                    if weakness.get("type") != "Primary":
                        continue
                    for description in weakness.get("description") or []:
                        if description.get("value", "").lower().startswith("cwe-"):
                            finding.cwe = description.get("value")
                            cwe_assigned = True
                            break
                    if cwe_assigned:
                        break
                severity = 5
                severity_assigned = False
                cvss_metrics = cve_info.get("metrics", {}) or {}
                for field in [
                    "cvssMetricV31",
                    "cvssMetricV30",
                    "cvssMetricV3",
                    "cvssMetricV2",
                ]:
                    metrics = cvss_metrics.get(field) or sum(
                        [
                            list(items)
                            for key, items in cvss_metrics.items()
                            if key.lower().startswith(field)
                        ],
                        [],
                    )
                    for cvss in metrics:
                        if cvss.get("type") == "Primary":
                            base_score = cvss.get("cvssData", {}).get("baseScore")
                            if base_score:
                                severity = base_score
                                severity_assigned = True
                                break
                    if severity_assigned:
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
