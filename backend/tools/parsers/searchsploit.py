"""Parser of the Searchsploit exploit search."""

from findings.models import Exploit
from tools.parsers.base import BaseParser


class Searchsploit(BaseParser):
    """Findings discovered by Searchsploit, read from its JSON report."""

    def _parse(self) -> None:
        """Create one exploit per result found in the Exploit Database."""
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
        # The exploits and the shellcodes are reported apart, but they are both exploits
        for key in ["RESULTS_EXPLOIT", "RESULTS_SHELLCODE"]:
            for exploit in data.get(key) or []:
                if exploit.get("Title"):
                    edb_id = exploit.get("EDB-ID")
                    self.create_finding(
                        Exploit,
                        title=exploit.get("Title"),
                        edb_id=int(edb_id) if edb_id else None,
                        # Searchsploit does not provide a direct link, so the Exploit-DB URL is built from the ID
                        reference=f"https://www.exploit-db.com/exploits/{edb_id}" if edb_id else None,
                    )
