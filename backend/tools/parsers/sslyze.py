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
    like Heartbleed, ROBOT, and CRIME attacks. SSLyze's report doesn't rate
    cipher suite strength itself, so weak ciphers are flagged by matching
    insecure_cipher_suites_patterns against the cipher suite names it reports.

    Attributes:
        protocol_versions (dict): Mapping of SSL/TLS protocols to versions
        insecure_cipher_suites_patterns (list): Name patterns of the cipher suites reported as insecure
        generic_tech (Technology | None): Generic TLS technology for findings
    """

    protocol_versions = {"ssl": ["2.0", "3.0"], "tls": ["1.0", "1.1", "1.2", "1.3"]}
    insecure_cipher_suites_patterns = ["_NULL_", "_RC4_", "_DES_", "_3DES_", "_MD5"]
    generic_tech: Technology | None = None

    def create_finding(
        self, finding_type: type[Finding], linked_finding: bool = False, **fields: Any
    ) -> Finding | None:
        """Create findings with automatic TLS technology association.

        Args:
            finding_type (type[Finding]): Type of finding to create
            linked_finding (bool): Whether the finding has already been linked to other findings
            **fields (Any): Field values for the finding

        Returns:
            Finding | None: Created finding instance with technology association, or None if
                           creation fails
        """
        if finding_type == Vulnerability and not fields.get("technology"):
            if not self.generic_tech:
                self.generic_tech = super().create_finding(Technology, name="TLS")
            fields["technology"] = self.generic_tech
            linked_finding = True
        return super().create_finding(finding_type, linked_finding, **fields)

    def _parse(self) -> None:
        """Parse SSLyze JSON output and extract SSL/TLS security findings.

        Processes JSON scan results to create Technology and Vulnerability findings
        for comprehensive SSL/TLS security analysis. Scan commands that were not
        scheduled or that failed report a null result and are treated as passing
        every check derived from them, since there's no data indicating otherwise.
        """
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
        for item in data.get("server_scan_results", []) or []:
            # SSLyze names this key differently across report versions, so both are tried
            result = item.get("scan_commands_results") or item.get("scan_result")
            if not result:
                continue
            # Scan commands that aren't scheduled or that fail have a null result, so they are
            # replaced by empty dicts and skipped by the checks below, which default to secure values
            result = {command: (value or {}).get("result") or {} for command, value in result.items()}
            for check, fields in [
                (
                    result.get("heartbleed", {}).get("is_vulnerable_to_heartbleed", False),
                    {"name": "Heartbleed", "cve": "CVE-2014-0160"},
                ),
                (
                    result.get("openssl_ccs_injection", {}).get("is_vulnerable_to_ccs_injection", False),
                    {"name": "OpenSSL CSS Injection", "cve": "CVE-2014-0224"},
                ),
                (
                    result.get("robot", {}).get("robot_result")
                    in ["VULNERABLE_STRONG_ORACLE", "VULNERABLE_WEAK_ORACLE"],
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
                    not result.get("session_renegotiation", {}).get("supports_secure_renegotiation", True)
                    or result.get("session_renegotiation", {}).get("is_vulnerable_to_client_renegotiation_dos", False),
                    {
                        "name": "Insecure TLS renegotiation supported",
                        "description": "Insecure TLS renegotiation supported",
                        "severity": Severity.MEDIUM,
                        # CWE CATEGORY: Permissions, Privileges, and Access Controls
                        "cwes": ["CWE-264"],
                    },
                ),
                (
                    result.get("tls_compression", {}).get("supports_compression", False),
                    {"name": "CRIME", "cve": "CVE-2012-4929"},
                ),
            ]:
                if check:
                    self.create_finding(Vulnerability, **fields)
            for protocol, versions in self.protocol_versions.items():
                for version in versions:
                    # SSLyze names each scan command's result key after its protocol and version,
                    # e.g. "tls_1_2_cipher_suites", which this string mirrors to look it up
                    cipher_suites = result.get(f"{protocol.lower()}_{version.replace('.', '_')}_cipher_suites", {}).get(
                        "accepted_cipher_suites", []
                    )
                    if cipher_suites:
                        technology = self.create_finding(Technology, name=protocol.upper(), version=version)
                        severity = Severity.HIGH
                        if protocol.lower() == "tls":
                            severity = Severity.MEDIUM
                            for cs in cipher_suites:
                                if any(c in cs["cipher_suite"]["name"] for c in self.insecure_cipher_suites_patterns):
                                    name = f"Insecure TLS {version} cipher suite {cs['cipher_suite']['name']} supported"
                                    self.create_finding(
                                        Vulnerability,
                                        linked_finding=True,
                                        technology=technology,
                                        name=name,
                                        description=name,
                                        severity=Severity.LOW,
                                        # CWE-326: Inadequate Encryption Strength
                                        cwes=["CWE-326"],
                                    )
                        if protocol.lower() == "ssl" or version not in ["1.2", "1.3"]:
                            name = f"Insecure {protocol.upper()} {version} supported"
                            self.create_finding(
                                Vulnerability,
                                linked_finding=True,
                                technology=technology,
                                name=name,
                                description=name,
                                severity=severity,
                                # CWE-326: Inadequate Encryption Strength
                                cwes=["CWE-326"],
                            )
            for deploy in result.get("certificate_info", {}).get("certificate_deployments") or []:
                # The certificate is valid only when it passes validation against every trust store
                if not all(validation["was_validation_successful"] for validation in deploy["path_validation_results"]):
                    self.create_finding(
                        Vulnerability,
                        linked_finding=self.generic_tech is not None,
                        technology=self.generic_tech,
                        name="Certificate validation error",
                        description="The certificate is not valid for the scanned host",
                        severity=Severity.LOW,
                        # CWE-295: Improper Certificate Validation
                        cwes=["CWE-295"],
                    )
                if deploy.get("verified_chain_has_legacy_symantec_anchor"):
                    self.create_finding(
                        Vulnerability,
                        linked_finding=self.generic_tech is not None,
                        technology=self.generic_tech,
                        name="Distrusted certificate authority",
                        description="The certificate was issued by a distrusted Symantec CA",
                        severity=Severity.MEDIUM,
                        # CWE-295: Improper Certificate Validation
                        cwes=["CWE-295"],
                    )
