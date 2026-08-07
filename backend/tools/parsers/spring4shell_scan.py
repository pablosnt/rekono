"""Parser of the Spring4Shell-Scan vulnerability scanner."""

from findings.models import Vulnerability
from tools.parsers.base import BaseParser


class Spring4shellscan(BaseParser):
    """Findings discovered by Spring4Shell-Scan, read from its output."""

    def _parse(self) -> None:
        """Create the Spring vulnerabilities that the target is affected by."""
        output = self.output or ""
        for name, cve in [("Spring Cloud RCE", "CVE-2022-22963"), ("Spring4Shell RCE", "CVE-2022-22965")]:
            if f"[!!!] Target Affected ({cve})" in output:
                self.create_finding(Vulnerability, name=name, cve=cve)
