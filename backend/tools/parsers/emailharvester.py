"""Parser of the EmailHarvester email discovery tool."""

from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Emailharvester(BaseParser):
    """Findings discovered by EmailHarvester, read from its report."""

    def _parse(self) -> None:
        """Create one OSINT finding per email address in the report."""
        emails = self.load_report_by_lines()
        for email in emails:
            email = email.strip()
            if email:
                self.create_finding(OSINT, data=email, data_type=OSINTDataType.EMAIL)
