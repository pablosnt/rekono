"""GitLeaks secret detection tool output parser.

Processes the GitLeaks JSON report, a list with one entry per discovered secret, to extract
exposed Credential findings, together with the Path and Vulnerability findings for the exposed
/.git/ endpoint itself. Also mines Credential findings for every Git contributor email found in
the dumped repository's commit history, not just the ones tied to a GitLeaks match.
"""

import subprocess
from dataclasses import dataclass
from typing import Any

from findings.enums import PathType, Severity
from findings.models import Credential, Finding, Path, Technology, Vulnerability
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

    def create_finding(
        self, finding_type: type[Finding], linked_finding: bool = False, **fields: Any
    ) -> Finding | None:
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
            finding = super().create_finding(
                finding_type, self.git_technology is not None, technology=self.git_technology, **fields
            )
        return finding

    def _parse(self) -> None:
        """Parse GitLeaks JSON output and extract secret findings.

        Processes JSON scan results to create Path, Vulnerability and Credential findings
        for Git repository exposure and discovered secrets.
        """
        if self.executor.git_directory_dumped:
            self.create_finding(Path, path=Path.clean_path("/.git"), type=PathType.ENDPOINT)
            self.create_finding(
                Vulnerability,
                name="Exposed git repository",
                description="Git repository is exposed in the endpoint /.git/ and it's possible to dump it and access the git history and source code",
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
                # Secret holds only the isolated token, so it is stored as the credential secret.
                # Match, the full matched text including the surrounding syntax, for example
                # token: "...", is kept in the context together with the rule that detected it.
                self.create_finding(
                    Credential,
                    secret=finding.get("Secret"),
                    context=f"/.git/ : '{finding.get('Match')}' detected by rule {finding.get('RuleID')} in {finding.get('File')}:{finding.get('StartLine')}",
                )
                # Email and Author are not present on every GitLeaks match, so both are coerced
                # to empty strings before being used
                email = (finding.get("Email") or "").strip()
                if email and email not in emails:
                    emails.add(email)
                    self._create_git_contributor_credential(email, (finding.get("Author") or "").strip())
            # GitLeaks only reports the emails of authors that committed a secret. The dumped repository
            # holds the whole commit history, so its author and committer emails are harvested as extra
            # credentials. This runs last so a git failure can't drop the secret findings parsed above.
            if self.executor.execution_directory.is_dir():
                try:
                    process = subprocess.run(
                        [
                            "git",
                            "-C",
                            str(self.executor.execution_directory),
                            "log",
                            "--all",
                            # Author and committer email/name per commit, separated by the unit separator
                            # byte so empty fields can't misalign the parsing
                            "--pretty=format:%ae%x1f%an%x1f%ce%x1f%cn",
                        ],
                        env=self.executor.environment,
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except Exception as ex:
                    self.executor.logger.warning(
                        f"[{self.executor.execution.configuration.tool.name}] {ex.__class__.__name__} error while "
                        f"harvesting emails from the git history of execution {self.executor.execution.id}: {ex!s}"
                    )
                    return
                for line in process.stdout.splitlines():
                    fields = line.split("\x1f")
                    if len(fields) != 4:
                        continue
                    author_email, author_name, committer_email, committer_name = fields
                    for email, name in [(author_email, author_name), (committer_email, committer_name)]:
                        email = (email or "").strip()
                        if email and email not in emails:
                            emails.add(email)
                            self._create_git_contributor_credential(email, (name or "").strip())

    def _create_git_contributor_credential(self, email: str | None, name: str | None) -> None:
        """Create a Credential for a Git contributor email, keeping their name in the context.

        Contributors reached through the GitLeaks report and through the commit history share the
        same context format, so both sources produce comparable credentials. Callers are responsible
        for skipping emails they have already seen, since this method creates a finding every time it
        is called. The contributor name, when known, is kept in the context to help identify the
        credential owner.

        Args:
            email (str | None): The contributor email address
            name (str | None): The contributor display name, if known
        """
        self.create_finding(
            Credential,
            email=email,
            context=f"/.git/ : Git contributor with name {name}" if name else "/.git/ : Git contributor",
        )
