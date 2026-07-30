"""Metasploit Framework exploit search output parser.

Processes Metasploit Framework search command output to extract available
exploit modules and references from the Metasploit database.
"""

from findings.models import Exploit
from tools.parsers.base import BaseParser


class Metasploit(BaseParser):
    """Parser for Metasploit Framework search command output.

    Extracts exploit module findings from Metasploit search results.
    Processes line-based output to identify available exploit modules
    with titles and reference paths within the Metasploit Framework.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Metasploit search output and extract exploit findings.

        Processes numbered search results to create Exploit findings for
        available Metasploit modules.
        """
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
