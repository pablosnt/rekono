"""Log4j-Scan Log4Shell vulnerability scanner output parser.

Processes Log4j-Scan plain text output to detect Log4Shell (CVE-2021-44228)
vulnerabilities in Java applications.
"""

from findings.models import Vulnerability
from tools.parsers.base import BaseParser


class Log4jscan(BaseParser):
    """Parser for Log4j-Scan plain text output.

    Detects Log4Shell vulnerability findings from Log4j-Scan output by searching
    for specific vulnerability indicators in the scan results. Creates vulnerability
    findings for confirmed Log4Shell detections.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Log4j-Scan output and extract Log4Shell vulnerability findings.

        Searches for Log4Shell vulnerability indicators in scan output and
        creates Vulnerability findings for confirmed detections.
        """
        if "[!!!] Targets Affected" in (self.output or ""):
            self.create_finding(Vulnerability, name="Log4Shell", cve="CVE-2021-44228")
