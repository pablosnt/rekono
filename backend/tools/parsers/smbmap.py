"""SMBMap SMB share enumeration tool output parser.

Processes SMBMap CSV output to extract discovered SMB shares and their
access permissions from network share enumeration scans.
"""

import csv

from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Smbmap(BaseParser):
    """Parser for SMBMap CSV output files.

    Extracts SMB share findings with access permissions from network share
    enumeration results. Processes CSV data to identify readable, writable,
    and inaccessible network shares.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse SMBMap CSV output and extract SMB share findings.

        Processes CSV enumeration results to create Path findings for
        discovered SMB shares with access permission details.
        """
        with self.report.open("r") as _report:
            reader = csv.reader(_report)
            # Discard the CSV header row
            next(reader)
            for row in reader:
                # The permissions column is the only reliable marker of a real share row,
                # so rows without a recognised permission value are skipped
                if any([keyword in row[2].upper() for keyword in ["READ", "WRITE", "NO_ACCESS"]]):
                    self.create_finding(
                        Path, path=row[1], extra_info=" - ".join([i for i in row[2:] if i]), type=PathType.SHARE
                    )
