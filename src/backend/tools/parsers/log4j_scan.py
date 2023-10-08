from findings.models import Vulnerability
from tools.parsers.base import BaseParser


class Log4jscan(BaseParser):
    def _parse_standard_output(self) -> None:
        if "[!!!] Targets Affected" in self.output:
            self.create_finding(Vulnerability, name="Log4Shell", cve="CVE-2021-44228")
