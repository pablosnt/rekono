from findings.models import Exploit
from tools.parsers.base import BaseParser


class Metasploit(BaseParser):
    def _parse(self) -> None:
        entry = 0
        for line in self.output.split("\n"):
            line = line.strip()
            if line and line.startswith(str(entry)):
                entry += 1
                data = [i.strip() for i in line.split("  ") if i]
                if not data[1].startswith("\_"):
                    self.create_finding(Exploit, title=data[-1], reference=data[1])
