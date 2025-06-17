from urllib.parse import urlparse

from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Dirsearch(BaseParser):
    def _parse_report(self) -> None:
        data = self._load_report_as_json_dict()
        for item in data.get("results", []):
            if "url" in item.keys():
                # New report format: just a list of findings
                url = urlparse(item.get("url", ""))
                if url.path:
                    self.create_finding(
                        Path, path=url.path.strip(), status=item.get("status", 0), type=PathType.ENDPOINT
                    )
            else:
                # Old report format: list of findings per target URL
                for findings in item.values():
                    if not isinstance(findings, list):
                        continue
                    for finding in findings:
                        if finding.get("path"):
                            self.create_finding(
                                Path,
                                path=finding.get("path").strip(),
                                status=finding.get("status", 0),
                                type=PathType.ENDPOINT,
                            )
