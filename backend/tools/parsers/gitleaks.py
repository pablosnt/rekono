"""GitLeaks secret detection tool output parser.

Processes GitLeaks JSON output to extract exposed secrets and credentials
from the commit history of dumped Git repositories.
"""

from dataclasses import dataclass
from typing import Any

from findings.enums import Severity
from findings.models import Credential, Finding, Technology, Vulnerability
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
        git_technology (Technology | None): Generic Git technology used to parent credentials
    """

    executor: GitleaksExecutor
    git_technology: Technology | None = None

    def create_finding(self, finding_type: type[Finding], linked_finding: bool = False, **fields: Any) -> Finding | None:
        """Create a finding, falling back to a generic Git technology for orphan credentials.

        A Credential can only be linked to a Technology, so the base parser normally links
        it to a technology detected during the execution. When no such technology exists the
        credential would be discarded (base returns None), so it is retried against a generic
        Git technology that acts as its parent finding.

        Args:
            finding_type (type[Finding]): The finding class to create
            linked_finding (bool): Whether the finding has already been linked to a parent
            **fields (Any): Field values for the finding

        Returns:
            Finding | None: The created or updated finding, or None if it could not be created
        """
        finding = super().create_finding(finding_type, linked_finding, **fields)
        # A discarded credential (no technology to link to) is retried against a generic Git technology
        if finding is None and finding_type == Credential and not fields.get("technology"):
            if not self.git_technology:
                self.git_technology = super().create_finding(Technology, name="Git")
            finding = super().create_finding(finding_type, self.git_technology is not None, technology=self.git_technology, **fields)
        return finding

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
                cwes=["CWE-527"],
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
