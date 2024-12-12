from findings.models import Exploit
from tools.parsers.base import BaseParser


class Searchsploit(BaseParser):
    def _parse_report(self) -> None:
        data = self._load_report_as_json()
        for exploit in data.get("RESULTS_EXPLOIT") or []:
            edb_id = exploit.get("EDB-ID")
            self.create_finding(
                Exploit,
                title=exploit.get("Title"),
                edb_id=int(edb_id) if edb_id else None,
                reference=(
                    f"https://www.exploit-db.com/exploits/{edb_id}" if edb_id else None
                ),
            )
