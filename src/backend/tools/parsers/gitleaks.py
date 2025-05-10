from findings.models import Credential
from tools.parsers.base import BaseParser


class Gitleaks(BaseParser):
    def _parse_report(self) -> None:
        data = self._load_report_as_json()
        emails = set()
        for finding in data:
            self.create_finding(
                Credential,
                secret=finding.get("Match"),
                context=f"/.git/ : {finding.get('File')} -> Line {finding.get('StartLine')}",
            )
            if finding.get("Email") and finding.get("Email") not in emails:
                emails.add(finding.get("Email"))
                self.create_finding(
                    Credential,
                    email=finding.get("Email"),
                    context=f"/.git/ : Email of the commit author {finding.get('Author')}",
                )
