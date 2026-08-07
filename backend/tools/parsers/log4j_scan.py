"""Parser of the Log4j-Scan vulnerability scanner."""

from findings.models import Vulnerability
from tools.parsers.base import BaseParser


class Log4jscan(BaseParser):
    """Findings discovered by Log4j-Scan, read from its output."""

    def _parse(self) -> None:
        """Create the Log4Shell vulnerability if the target is affected by it."""
        if "[!!!] Targets Affected" in (self.output or ""):
            self.create_finding(Vulnerability, name="Log4Shell", cve="CVE-2021-44228")
