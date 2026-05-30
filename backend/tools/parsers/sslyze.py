"""SSLyze SSL/TLS security scanner output parser.

Processes SSLyze JSON output to extract comprehensive SSL/TLS security findings
including protocol vulnerabilities, cipher suite weaknesses, and certificate issues.
"""

from typing import Any

from findings.enums import Severity
from findings.models import Finding, Technology, Vulnerability
from tools.parsers.base import BaseParser


class Sslyze(BaseParser):
    """Parser for SSLyze JSON output files.

    Extracts detailed SSL/TLS security findings including supported protocols,
    cipher suites, certificate validation issues, and known vulnerabilities
    like Heartbleed, ROBOT, and CRIME attacks.

    Attributes:
        protocol_versions (dict): Mapping of SSL/TLS protocols to versions
        generic_tech (Technology | None): Generic TLS technology for findings
    """

    protocol_versions = {"ssl": ["2.0", "3.0"], "tls": ["1.0", "1.1", "1.2", "1.3"]}
    generic_tech: Technology | None = None

    def create_finding(
        self, finding_type: type[Finding], linked_finding: bool = False, **fields: Any
    ) -> Finding | None:
        """Create findings with automatic TLS technology association.

        Args:
            finding_type (type[Finding]): Type of finding to create
            **fields (Any): Field values for the finding

        Returns:
            Finding: Created finding instance with technology association
        """
        if finding_type == Vulnerability and not fields.get("technology"):
            if not self.generic_tech:
                self.generic_tech = super().create_finding(Technology, name="Generic TLS")
            fields["technology"] = self.generic_tech
            linked_finding = True
        return super().create_finding(finding_type, linked_finding, **fields)

    def _parse(self) -> None:
        """Parse SSLyze JSON output and extract SSL/TLS security findings.

        Processes JSON scan results to create Technology and Vulnerability findings
        for comprehensive SSL/TLS security analysis.
        """
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
        for item in data.get("server_scan_results", []) or []:
            result = item.get("scan_commands_results", item["scan_result"])
            if not result:
                continue
            for check, fields in [
                (
                    result["heartbleed"]["result"]["is_vulnerable_to_heartbleed"],
                    {"name": "Heartbleed", "cve": "CVE-2014-0160"},
                ),
                (
                    result["openssl_ccs_injection"]["result"]["is_vulnerable_to_ccs_injection"],
                    {"name": "OpenSSL CSS Injection", "cve": "CVE-2014-0224"},
                ),
                (
                    result["robot"]["result"]["robot_result"] in ["VULNERABLE_STRONG_ORACLE", "VULNERABLE_WEAK_ORACLE"],
                    {
                        "name": "ROBOT",
                        "description": "Return Of the Bleichenbacher Oracle Threat",
                        "severity": Severity.MEDIUM,
                        # CWE-203: Observable Discrepancy
                        "cwes": ["CWE-203"],
                        "reference": "https://www.robotattack.org/",
                    },
                ),
                (
                    not result["session_renegotiation"]["result"]["supports_secure_renegotiation"]
                    or result["session_renegotiation"]["result"]["is_vulnerable_to_client_renegotiation_dos"],
                    {
                        "name": "Insecure TLS renegotiation supported",
                        "description": "Insecure TLS renegotiation supported",
                        "severity": Severity.MEDIUM,
                        # CWE CATEGORY: Permissions, Privileges, and Access Controls
                        "cwes": ["CWE-264"],
                    },
                ),
                (
                    result["tls_compression"]["result"]["supports_compression"],
                    {"name": "CRIME", "cve": "CVE-2012-4929"},
                ),
            ]:
                if check:
                    self.create_finding(Vulnerability, **fields)
            for protocol, versions in self.protocol_versions.items():
                for version in versions:
                    cipher_suites = (
                        result.get(
                            f"{protocol.lower()}_{version.replace('.', '_')}_cipher_suites",
                            {},
                        )
                        .get("result", {})
                        .get("accepted_cipher_suites", [])
                    )
                    if cipher_suites:
                        technology = self.create_finding(Technology, name=protocol.upper(), version=version)
                        severity = Severity.HIGH
                        if protocol.lower() == "tls":
                            severity = Severity.MEDIUM
                            for cs in cipher_suites:
                                if "_RC4_" in cs["cipher_suite"]["name"]:
                                    self.create_finding(
                                        Vulnerability,
                                        linked_finding=True,
                                        technology=technology,
                                        name="Insecure cipher suite supported",
                                        description=f"TLS {technology.version if technology else ''} {cs['cipher_suite']['name']}",
                                        severity=Severity.LOW,
                                        # CWE-326: Inadequate Encryption Strength
                                        cwes=["CWE-326"],
                                    )
                        if protocol.lower() == "ssl" or version not in ["1.2", "1.3"]:
                            self.create_finding(
                                Vulnerability,
                                linked_finding=True,
                                technology=technology,
                                name=f"Insecure {protocol.upper()} version supported",
                                description=f"{protocol.upper()} {version} is supported",
                                severity=severity,
                                # CWE-326: Inadequate Encryption Strength
                                cwes=["CWE-326"],
                            )
            for deploy in result["certificate_info"]["result"]["certificate_deployments"] or []:
                if not deploy["leaf_certificate_subject_matches_hostname"]:
                    self.create_finding(
                        Vulnerability,
                        linked_finding=self.generic_tech is not None,
                        technology=self.generic_tech,
                        name="Certificate subject error",
                        description="Certificate subject doesn't match hostname",
                        severity=Severity.INFO,
                        # CWE-295: Improper Certificate Validation
                        cwes=["CWE-295"],
                    )
