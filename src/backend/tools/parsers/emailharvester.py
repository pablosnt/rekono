from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Emailharvester(BaseParser):
    def _parse(self) -> None:
        emails = self.load_report_by_lines()
        for email in emails:
            email = email.strip()
            if email:
                self.create_finding(OSINT, data=email, data_type=OSINTDataType.EMAIL)
