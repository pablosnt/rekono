from findings.models import Exploit
from tools.parsers.base import BaseParser


class Searchsploit(BaseParser):
    def _parse(self) -> None:
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
