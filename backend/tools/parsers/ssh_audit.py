"""SSH Audit SSH security scanner output parser.

Processes the SSH Audit JSON report to extract the SSH server Technology from its banner and a
Vulnerability finding for each insecure encryption, key exchange, host key or MAC algorithm the
report flags. CVE identifiers referenced in the report's algorithm notes are also extracted and
reported as their own Vulnerability findings.
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

        Creates a Technology finding from the SSH banner and a Vulnerability finding for every
        enc, kex, key or mac algorithm SSH Audit flagged with a fail or warn note (algorithms
        with only info notes are skipped). CVE identifiers are extracted with a regex from the
        free text of those notes, since SSH Audit leaves its own top-level cves field empty for
        algorithm-level advisories.
        """
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
        # banner.software follows a "<name>_<version>" format (e.g. "libssh_0.8.1"); default to
        # a bare "_" so the split still yields two empty strings when banner or software is missing
        name, version = data.get("banner", {}).get("software", "_").split("_", 1)
        technology = self.create_finding(Technology, name=name, version=version)
        cves = set([])
        for root in ["enc", "kex", "key", "mac"]:
            for item in data.get(root) or []:
                # Notes are lowercase sentence fragments in the report, capitalized here for a
                # readable Vulnerability description
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
                        cwes=["CWE-326"],
                    )
                # CVE ids only ever appear inline inside note text (e.g. "... (CVE-2023-48795)"),
                # not as structured data on the algorithm entry, so they are pulled out with a regex
                for note in notes:
                    for cve in re.findall(Regex.CVE.value, note):
                        cves.add(cve)
        for cve in cves:
            self.create_finding(Vulnerability, linked_finding=True, technology=technology, name=cve, cve=cve)
