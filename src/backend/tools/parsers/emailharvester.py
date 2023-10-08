from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Emailharvester(BaseParser):
    def _parse_report(self) -> None:
        with open(self.report, "r", encoding="utf-8") as report:
            emails = report.readlines()
        for email in emails:
            email = email.strip()
            if email:
                self.create_finding(OSINT, data=email, data_type=OSINTDataType.EMAIL)
