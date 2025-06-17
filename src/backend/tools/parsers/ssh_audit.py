import re

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from security.validators.input_validator import Regex
from tools.parsers.base import BaseParser


class Sshaudit(BaseParser):
    def _parse_report(self):
        data = self._load_report_as_json_dict()
        name, version = data.get("banner", {}).get("software", "_").split("_", 1)
        technology = self.create_finding(Technology, name=name, version=version)
        cves = set([])
        for root in ["enc", "kex", "key", "mac"]:
            for item in data.get(root) or []:
                notes = [
                    note[0].upper() + note[1:]
                    for note in (item.get("notes", {}).get("fail", []) + item.get("notes", {}).get("warn", []))
                ]
                if "fail" in item.get("notes", {}) or "warn" in item.get("notes", {}):
                    self.create_finding(
                        Vulnerability,
                        technology=technology,
                        name=f"Insecure {root} algorithm: {item.get('algorithm')}",
                        description="\n".join(notes),
                        severity=Severity.MEDIUM if "fail" in item.get("notes", {}) else Severity.LOW,
                        # CWE-326: Inadequate Encryption Strength
                        cwe="CWE-326",
                    )
                for note in notes:
                    for cve in re.findall(Regex.CVE.value, note):
                        cves.add(cve)
        for cve in cves:
            self.create_finding(Vulnerability, technology=technology, name=cve, cve=cve)
