from findings.models import Exploit
from tools.parsers.base import BaseParser


class Metasploit(BaseParser):
    def _parse_standard_output(self) -> None:
        entry = 0
        for line in self.output.split("\n"):
            if line.strip() and line.strip().startswith(str(entry)):
                entry += 1
                data = [i.strip() for i in line.strip().split("  ") if i]
                if not data[1].startswith("\_"):
                    self.create_finding(Exploit, title=data[-1], reference=data[1])
