"""Searchsploit exploit database search tool output parser.

Processes Searchsploit JSON output to extract exploit and shellcode findings
from Exploit Database searches.
"""

from findings.models import Exploit
from tools.parsers.base import BaseParser


class Searchsploit(BaseParser):
    """Parser for Searchsploit JSON output files.

    Extracts exploit and shellcode findings from Exploit Database search results.
    Processes both exploit and shellcode entries with EDB-ID references and
    direct links to Exploit Database.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Searchsploit JSON output and extract exploit findings.

        Processes JSON search results to create Exploit findings for
        discovered exploits and shellcodes from the Exploit Database.
        """
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
        for key in ["RESULTS_EXPLOIT", "RESULTS_SHELLCODE"]:
            for exploit in data.get(key) or []:
                if exploit.get("Title"):
                    edb_id = exploit.get("EDB-ID")
                    self.create_finding(
                        Exploit,
                        title=exploit.get("Title"),
                        edb_id=int(edb_id) if edb_id else None,
                        reference=f"https://www.exploit-db.com/exploits/{edb_id}" if edb_id else None,
                    )
