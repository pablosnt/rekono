"""EmailHarvester email discovery tool output parser.

Processes EmailHarvester line-based output to extract discovered email addresses
from OSINT email enumeration and reconnaissance operations.
"""

from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Emailharvester(BaseParser):
    """Parser for EmailHarvester line-based output files.

    Extracts email address findings from EmailHarvester output files.
    Processes line-separated email addresses discovered during OSINT
    reconnaissance and email enumeration operations.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse EmailHarvester output and extract email findings.

        Processes line-based output to create OSINT findings for
        discovered email addresses.
        """
        emails = self.load_report_by_lines()
        for email in emails:
            email = email.strip()
            if email:
                self.create_finding(OSINT, data=email, data_type=OSINTDataType.EMAIL)
