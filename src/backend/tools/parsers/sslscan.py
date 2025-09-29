"""SSLScan SSL/TLS security scanner output parser.

Processes SSLScan XML output to extract SSL/TLS protocol vulnerabilities,
insecure cipher suites, and protocol configuration findings.
"""

from typing import Any

from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Technology, Vulnerability
from tools.parsers.base import BaseParser


class Sslscan(BaseParser):
    """Parser for SSLScan XML output files.

    Extracts SSL/TLS security findings including supported protocols, cipher suites,
    and known vulnerabilities like Heartbleed. Associates findings with detected
    SSL/TLS technology versions for comprehensive analysis.

    Attributes:
        technologies (list[Technology]): List of detected SSL/TLS protocol technologies
    """

    technologies: list[Technology] = []

    def create_finding(self, finding_type: type[Finding], linked_finding: bool = False, **fields: Any) -> Finding:
        """Create findings with automatic SSL/TLS technology association.

        Args:
            finding_type (type[Finding]): Type of finding to create
            **fields (Any): Field values for the finding

        Returns:
            Finding: Created finding instance with technology association
        """
        if finding_type == Vulnerability and not fields.get("technology") and fields.get("sslversion"):
            search = [t for t in self.technologies if f"{t.name}v{t.version}" == fields.get("sslversion")]
            if search:
                fields["technology"] = search[0]
                linked_finding = True
            fields.pop("sslversion")
        return super().create_finding(finding_type, linked_finding, **fields)

    def _parse(self) -> None:
        """Parse SSLScan XML output and extract SSL/TLS security findings.

        Processes XML scan results to create Technology and Vulnerability findings
        for SSL/TLS protocols, cipher suites, and security issues.
        """
        root = self.load_xml_report()
        if not root:
            return
        for test in root.findall("ssltest"):
            for item in test:
                if item.tag == "protocol" and item.attrib["enabled"] == "1":
                    technology = self.create_finding(
                        Technology, name=item.attrib["type"].upper(), version=item.attrib["version"]
                    )
                    self.technologies.append(technology)
                    if technology.name != "TLS" or technology.version not in ["1.2", "1.3"]:
                        self.create_finding(
                            Vulnerability,
                            linked_finding=True,
                            technology=technology,
                            name=f"Insecure {technology.name} version supported",
                            description=f"{technology.name} {technology.version} is supported",
                            severity=Severity.MEDIUM if technology.name == "TLS" else Severity.HIGH,
                            # CWE-326: Inadequate Encryption Strength
                            cwe="CWE-326",
                        )
                else:
                    for check, fields in [
                        (
                            item.tag == "renegotiation"
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
                            item.tag == "heartbleed" and item.attrib["vulnerable"] == "1",
                            {"name": f"Heartbleed in {item.attrib.get('sslversion')}", "cve": "CVE-2014-0160"},
                        ),
                        (
                            item.tag == "cipher" and item.attrib["strength"] not in ["acceptable", "strong"],
                            {
                                "name": "Insecure cipher suite supported",
                                "description": f"{item.attrib.get('sslversion')} {item.attrib.get('cipher')} status={item.attrib.get('status')} strength={item.attrib.get('strength')}",
                                "severity": Severity.LOW,
                                # CWE-326: Inadequate Encryption Strength
                                "cwe": "CWE-326",
                            },
                        ),
                    ]:
                        if check:
                            self.create_finding(Vulnerability, **fields)
