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
        for line in self.output.split("\n"):
            line = line.strip()
            if line and line.startswith(str(entry)):
                entry += 1
                data = [i.strip() for i in line.split("  ") if i]
                if not data[1].startswith("\_"):
                    self.create_finding(Exploit, title=data[-1], reference=data[1])
