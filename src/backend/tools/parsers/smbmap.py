from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Smbmap(BaseParser):
    def _parse_standard_output(self) -> None:
        for line in self.output.split("\n"):
            data = line.strip()
            if data and ("READ" in data or "WRITE" in data or "NO ACCESS" in data):
                share = [i.strip() for i in data.split("  ") if i.strip()]
                self.create_finding(
                    Path,
                    path=share[0],
                    extra=f"[{share[1]}] {share[2]}" if len(share) >= 3 else share[1],
                    type=PathType.SHARE,
                )
