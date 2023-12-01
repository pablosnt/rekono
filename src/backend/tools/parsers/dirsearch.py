import json

from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Dirsearch(BaseParser):
    def _parse_report(self) -> None:
        data = self._load_report_as_json()
        for url in data.get("results", []):
            for item in url.values():
                for endpoint in item:
                    self.create_finding(
                        Path,
                        path=endpoint.get("path", "").strip(),
                        status=endpoint.get("status", 0),
                        type=PathType.ENDPOINT,
                    )
