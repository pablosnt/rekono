"""GitLeaks secret detection tool output parser.

Processes GitLeaks JSON output to extract exposed secrets and credentials
from Git repository dumps and source code analysis.
"""

from dataclasses import dataclass

from findings.enums import Severity
from findings.models import Credential, Vulnerability
from tools.executors.gitleaks import Gitleaks as GitleaksExecutor
from tools.parsers.base import BaseParser


@dataclass
class Gitleaks(BaseParser):
    """Parser for GitLeaks JSON output files.

    Extracts secret detection findings including exposed credentials, API keys,
    and sensitive information from Git repositories. Handles both Git repository
    exposure vulnerabilities and individual secret findings.

    Attributes:
        executor (GitleaksExecutor): GitLeaks-specific executor instance
    """

    executor: GitleaksExecutor

    def _parse(self) -> None:
        """Parse GitLeaks JSON output and extract secret findings.

        Processes JSON scan results to create Vulnerability and Credential findings
        for Git repository exposure and discovered secrets.
        """
        if self.executor.git_directory_dumped:
            self.create_finding(
                Vulnerability,
                name="Git source code exposure",
                description="Source code is exposed in the endpoint /.git/ and it's possible to dump it as a git repository",
                severity=Severity.HIGH,
                # CWE-527: Exposure of Version-Control Repository to an Unauthorized Control Sphere
                cwe="CWE-527",
                reference="https://iosentrix.com/blog/git-source-code-disclosure-vulnerability/",
            )
        data = self.load_json_report()
        if not data or not isinstance(data, list):
            return
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
                    context=f"/.git/ : Author of the commit {finding.get('Commit')} whose name is {finding.get('Author')}",
                )
