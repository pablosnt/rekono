"""Parser of the SMBMap share enumeration tool."""

import csv

from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Smbmap(BaseParser):
    """Findings discovered by SMBMap, read from its CSV report."""

    def _parse(self) -> None:
        """Create one path per SMB share found, with the access allowed to it."""
        with self.report.open("r") as _report:
            reader = csv.reader(_report)
            next(reader)
            for row in reader:
                # The permissions column is the only reliable marker of a real share row,
                # so rows without a recognised permission value are skipped
                if any([keyword in row[2].upper() for keyword in ["READ", "WRITE", "NO_ACCESS"]]):
                    self.create_finding(
                        Path, path=row[1], extra_info=" - ".join([i for i in row[2:] if i]), type=PathType.SHARE
                    )
