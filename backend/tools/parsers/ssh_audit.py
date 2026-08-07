"""Parser of the SSH Audit server scanner."""

import re

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from security.validators.input_validator import Regex
from tools.parsers.base import BaseParser


class Sshaudit(BaseParser):
    """Findings discovered by SSH Audit, read from its JSON report."""

    def _parse(self) -> None:
        """Create the SSH server and one vulnerability per insecure algorithm.

        The algorithms that SSH Audit only comments on are left out, since a note
        that isn't a warning says that the algorithm is fine.
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
