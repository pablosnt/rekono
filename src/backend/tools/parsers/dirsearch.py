from urllib.parse import urlparse

from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Dirsearch(BaseParser):
    def _parse_report(self) -> None:
        data = self._load_report_as_json()
        for item in data.get("results", []):
            url = urlparse(item.get("url", ""))
            if url.path:
                self.create_finding(
                    Path,
                    path=url.path.strip(),
                    status=item.get("status", 0),
                    type=PathType.ENDPOINT,
                )
