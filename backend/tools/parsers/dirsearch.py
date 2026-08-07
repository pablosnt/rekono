"""Parser of the Dirsearch path enumeration tool."""

from urllib.parse import urlparse

from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Dirsearch(BaseParser):
    """Findings discovered by Dirsearch, read from its JSON report."""

    def _parse(self) -> None:
        """Create one path per endpoint found in the report."""
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
        for item in data.get("results", []):
            if "url" in item.keys():
                # Current format: each result is already its own finding, with its own "url"
                url = urlparse(item.get("url", ""))
                if url.path:
                    self.create_finding(
                        Path,
                        path=Path.clean_path(url.path.strip()),
                        status=item.get("status", 0),
                        type=PathType.ENDPOINT,
                    )
            else:
                # Legacy format: "results" has a single entry keyed by the scanned base URL,
                # whose value is the list of findings discovered under it
                for findings in item.values():
                    if not isinstance(findings, list):
                        continue
                    for finding in findings:
                        if finding.get("path"):
                            self.create_finding(
                                Path,
                                path=Path.clean_path(finding.get("path").strip()),
                                status=finding.get("status", 0),
                                type=PathType.ENDPOINT,
                            )
