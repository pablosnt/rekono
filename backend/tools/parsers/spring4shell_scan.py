"""Spring4Shell-Scan vulnerability scanner output parser.

Processes Spring4Shell-Scan plain text output to detect Spring Framework
vulnerabilities including Spring4Shell and Spring Cloud RCE vulnerabilities.
"""

from findings.models import Vulnerability
from tools.parsers.base import BaseParser


class Spring4shellscan(BaseParser):
    """Parser for Spring4Shell-Scan plain text output.

    Detects Spring Framework vulnerability findings from Spring4Shell-Scan output
    by searching for specific vulnerability indicators. Creates vulnerability findings
    for Spring4Shell and Spring Cloud RCE detections.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Spring4Shell-Scan output and extract Spring vulnerability findings.

        Searches for Spring Framework vulnerability indicators in scan output and
        creates Vulnerability findings for confirmed detections.
        """
        output = self.output or ""
        for name, cve in [("Spring Cloud RCE", "CVE-2022-22963"), ("Spring4Shell RCE", "CVE-2022-22965")]:
            if f"[!!!] Target Affected ({cve})" in output:
                self.create_finding(Vulnerability, name=name, cve=cve)
