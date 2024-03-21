from django.core.exceptions import ValidationError
from django.forms import EmailField

from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Emailfinder(BaseParser):
    def _parse_standard_output(self) -> None:
        checker = EmailField()
        for line in self.output.split("\n"):
            line = line.strip()
            if line:
                try:
                    checker.clean(line)
                    self.create_finding(OSINT, data=line, data_type=OSINTDataType.EMAIL)
                except ValidationError:
                    pass
