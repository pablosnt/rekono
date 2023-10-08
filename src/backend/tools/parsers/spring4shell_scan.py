from findings.models import Vulnerability
from tools.parsers.base import BaseParser


class Spring4shellscan(BaseParser):
    def _parse_standard_output(self) -> None:
        for search, name, cve in [
            (
                "[!!!] Target Affected (CVE-2022-22963)",
                "Spring Cloud RCE",
                "CVE-2022-22963",
            ),
            (
                "[!!!] Target Affected (CVE-2022-22965)",
                "Spring4Shell RCE",
                "CVE-2022-22965",
            ),
        ]:
            if search in self.output:
                self.create_finding(Vulnerability, name=name, cve=cve)
