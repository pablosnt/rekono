"""EmailFinder email discovery tool output parser.

Processes EmailFinder plain text output to extract and validate email addresses
from OSINT email enumeration results.
"""

from django.core.exceptions import ValidationError
from django.forms import EmailField

from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Emailfinder(BaseParser):
    """Parser for EmailFinder plain text output.

    Extracts and validates email addresses from EmailFinder output using Django's
    built-in email validation. Creates OSINT findings for discovered email addresses
    from email enumeration and reconnaissance operations.
    
    Attributes:
        Inherits all attributes from BaseParser
    """
    def _parse(self) -> None:
        """Parse EmailFinder output and extract email findings.
        
        Processes line-based output to validate and create OSINT findings
        for discovered email addresses.
        """
        checker = EmailField()
        for line in self.output.split("\n"):
            line = line.strip()
            if line:
                try:
                    checker.clean(line)
                    self.create_finding(OSINT, data=line, data_type=OSINTDataType.EMAIL)
                except ValidationError:
                    pass
