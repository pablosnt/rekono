from typing import Any

from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Technology, Vulnerability
from tools.parsers.base import BaseParser


class Sslscan(BaseParser):
    technologies: list[Technology] = []

    def create_finding(self, finding_type: Finding, **fields: Any) -> Finding:
        if finding_type == Vulnerability and not fields.get("technology") and fields.get("sslversion"):
            search = [t for t in self.technologies if f"{t.name}v{t.version}" == fields.get("sslversion")]
            fields["technology"] = search[0] if search else None
            fields.pop("sslversion")
        return super().create_finding(finding_type, **fields)

    def _parse_report(self) -> None:
        try:
            root = self._load_report_as_xml()
        except Exception:
            return
        for test in root.findall("ssltest"):
            for item in test:
                if item.tag == "protocol" and item.attrib["enabled"] == "1":
                    technology = self.create_finding(
                        Technology,
                        name=item.attrib["type"].upper(),
                        version=item.attrib["version"],
                    )
                    self.technologies.append(technology)
                    if technology.name != "TLS" or technology.version not in [
                        "1.2",
                        "1.3",
                    ]:
                        self.create_finding(
                            Vulnerability,
                            technology=technology,
                            name=f"Insecure {technology.name} version supported",
                            description=f"{technology.name} {technology.version} is supported",
                            severity=(Severity.MEDIUM if technology.name == "TLS" else Severity.HIGH),
                            # CWE-326: Inadequate Encryption Strength
                            cwe="CWE-326",
                        )
                else:
                    for check, fields in [
                        (
                            lambda: item.tag == "renegotiation"
                            and item.attrib["supported"] == "1"
                            and item.attrib["secure"] != "1",
                            {
                                "name": "Insecure TLS renegotiation supported",
                                "description": "Insecure TLS renegotiation supported",
                                "severity": Severity.MEDIUM,
                                # CWE CATEGORY: Permissions, Privileges, and Access Controls
                                "cwe": "CWE-264",
                            },
                        ),
                        (
                            lambda: item.tag == "heartbleed" and item.attrib["vulnerable"] == "1",
                            {
                                "name": f"Heartbleed in {item.attrib.get('sslversion')}",
                                "cve": "CVE-2014-0160",
                            },
                        ),
                        (
                            lambda: item.tag == "cipher"
                            and item.attrib["strength"]
                            not in [
                                "acceptable",
                                "strong",
                            ],
                            {
                                "name": "Insecure cipher suite supported",
                                "description": f"{item.attrib.get('sslversion')} {item.attrib.get('cipher')} status={item.attrib.get('status')} strength={item.attrib.get('strength')}",
                                "severity": Severity.LOW,
                                # CWE-326: Inadequate Encryption Strength
                                "cwe": "CWE-326",
                            },
                        ),
                    ]:
                        if check():
                            self.create_finding(Vulnerability, **fields)
