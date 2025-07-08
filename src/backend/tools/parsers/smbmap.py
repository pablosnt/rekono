import csv

from findings.enums import PathType
from findings.models import Path
from tools.parsers.base import BaseParser


class Smbmap(BaseParser):
    def _parse_report(self) -> None:
        with self.report.open("r") as _report:
            reader = csv.reader(_report)
            next(reader)
            for row in reader:
                if any([keyword.upper() in row[2].upper() for keyword in ["READ", "WRITE", "NO_ACCESS"]]):
                    self.create_finding(
                        Path, path=row[1], extra_info=" - ".join([i for i in row[2:] if i]), type=PathType.SHARE
                    )
