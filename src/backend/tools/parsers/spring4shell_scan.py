from findings.models import Vulnerability
from tools.parsers.base import BaseParser


class Spring4shellscan(BaseParser):
    def _parse_standard_output(self) -> None:
        for name, cve in [("Spring Cloud RCE", "CVE-2022-22963"), ("Spring4Shell RCE", "CVE-2022-22965")]:
            if f"[!!!] Target Affected ({cve})" in self.output:
                self.create_finding(Vulnerability, name=name, cve=cve)
