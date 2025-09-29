"""SSH Audit SSH security scanner output parser.

Processes SSH Audit JSON output to extract SSH server technology fingerprints
and security vulnerabilities from SSH configuration analysis.
"""

import re

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from security.validators.input_validator import Regex
from tools.parsers.base import BaseParser


class Sshaudit(BaseParser):
    """Parser for SSH Audit JSON output files.

    Extracts SSH server technology and security findings including insecure
    encryption algorithms, key exchange methods, and known vulnerabilities.
    Processes comprehensive SSH configuration security analysis.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse SSH Audit JSON output and extract SSH security findings.

        Processes JSON scan results to create Technology and Vulnerability findings
        for SSH server configuration and security issues.
        """
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
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
                        linked_finding=True,
                        technology=technology,
                        name=f"Insecure {root.upper()} algorithm: {item.get('algorithm')}",
                        description="\n".join(notes),
                        severity=Severity.MEDIUM if "fail" in item.get("notes", {}) else Severity.LOW,
                        # CWE-326: Inadequate Encryption Strength
                        cwe="CWE-326",
                    )
                for note in notes:
                    for cve in re.findall(Regex.CVE.value, note):
                        cves.add(cve)
        for cve in cves:
            self.create_finding(Vulnerability, linked_finding=True, technology=technology, name=cve, cve=cve)
