from typing import Any

from executions.models import Execution
from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.platforms import BaseIntegration
from platforms.nvdnist.models import NvdNistSettings


class NvdNist(BaseIntegration):
    finding_types = [Vulnerability]
    settings = NvdNistSettings.objects.first()
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
    def is_api_token_available(self) -> bool:
        if self.settings.secret is None:
            return False
        try:
            # Test the API token by getting Log4Shell information
            self._get_cve("CVE-2021-44228")
            return True
        except Exception:
            return False

    def _get_cve(self, cve: str) -> dict[str, Any]:
        if self.settings.secret is not None:
            return self._request(self.session.get, self.url.format(cve=cve), headers={"apiKey": self.settings.secret})
        return self._request(self.session.get, self.url.format(cve=cve))

    def _process_finding(self, execution: Execution, finding: Vulnerability) -> None:
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
                        [list(items) for key, items in cvss_metrics.items() if key.lower().startswith(field)], []
                    ):
                        if cvss.get("type", "").lower() == type:
                            base_score = cvss.get("cvssData", {}).get("baseScore")
                            if base_score:
                                severity = base_score
                                # TODO: Save CVSS version, vector and baseScore in the vulnerability model
                                finding.severity = [
                                    k for k, v in self.cvss_mapping.items() if severity >= v[0] and severity < v[1]
                                ][0]
                                update.extend(["severity"])
                                break
                    if severity > 0:
                        break
        finding.reference = self.reference.format(cve=finding.cve)
        finding.save(update_fields=update)

    def is_finding_processable(self, finding: Finding) -> bool:
        return super().is_finding_processable(finding) and finding.cve is not None
