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
        # The whole report is one JSON object; bail out if it failed to parse or came back
        # in an unexpected shape
        if not data or not isinstance(data, dict):
            return
        # Exploits and shellcodes are reported under separate top-level keys but handled the same way
        for key in ["RESULTS_EXPLOIT", "RESULTS_SHELLCODE"]:
            for exploit in data.get(key) or []:
                # Title is required on the Exploit model, so entries without one are skipped
                if exploit.get("Title"):
                    # EDB-ID arrives as a numeric string, so it is cast to int for storage
                    edb_id = exploit.get("EDB-ID")
                    self.create_finding(
                        Exploit,
                        title=exploit.get("Title"),
                        edb_id=int(edb_id) if edb_id else None,
                        # Searchsploit does not provide a direct link, so the Exploit-DB URL is built from the ID
                        reference=f"https://www.exploit-db.com/exploits/{edb_id}" if edb_id else None,
                    )
