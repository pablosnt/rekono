"""Parser of the Metasploit Framework exploit search."""

from findings.models import Exploit
from tools.parsers.base import BaseParser


class Metasploit(BaseParser):
    """Findings discovered by Metasploit, read from its search output."""

    def _parse(self) -> None:
        """Create one exploit per module found in the search results."""
        entry = 0
        for line in (self.output or "").split("\n"):
            line = line.strip()
            # Result rows are numbered from 0 upwards, so matching the next expected number
            # keeps the banner and the column headers out of the results
            if line and line.startswith(str(entry)):
                entry += 1
                # The table is space aligned, so two or more spaces separate the columns
                data = [i.strip() for i in line.split("  ") if i]
                # Rows whose reference starts with \_ are the target variants listed under a
                # module, and recording them would duplicate the module they belong to
                if not data[1].startswith("\_"):
                    self.create_finding(Exploit, title=data[-1], reference=data[1])
