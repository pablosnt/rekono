"""Dirsearch web directory enumeration tool output parser.

Processes Dirsearch JSON output to extract discovered web paths and endpoints
from directory brute force enumeration scans.
"""

from urllib.parse import urlparse

from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Dirsearch(BaseParser):
    """Parser for Dirsearch JSON output files.

    Extracts discovered web paths and endpoints from Dirsearch directory
    enumeration results. Supports both legacy and current JSON output formats
    with automatic format detection.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Dirsearch JSON output and extract path findings.

        Processes JSON enumeration results to create Path findings for discovered web
        directories and endpoints. Detects which of the two known "results" layouts
        the report uses and reads it accordingly.
        """
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
