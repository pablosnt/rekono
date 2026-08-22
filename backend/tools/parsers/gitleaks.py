"""Parser of the GitLeaks secret scanner."""

import subprocess
from dataclasses import dataclass
from typing import Any

from findings.enums import PathType, Severity
from findings.models import Credential, Finding, Path, Technology, Vulnerability
from tools.executors.gitleaks import Gitleaks as GitleaksExecutor
from tools.parsers.base import BaseParser


@dataclass
class Gitleaks(BaseParser):
    """Findings discovered by GitLeaks, read from its JSON report.

    Besides the secrets, the exposed repository itself is reported, since being
    able to read the source code and its history is a vulnerability on its own.

    Attributes:
        executor: Executor that downloaded the repository and ran GitLeaks.
        git_technology: Technology that the credentials belong to when nothing
          else was discovered in the target to link them to.
    """

    executor: GitleaksExecutor
    git_technology: Technology | None = None

    def create_finding(
        self, finding_type: type[Finding], linked_finding: bool = False, **fields: Any
    ) -> Finding | None:
        """Create a finding, keeping the credentials that have no technology.

        Args:
            finding_type: Kind of finding to create.
            linked_finding: Whether the caller already linked the finding.
            **fields: Data of the finding.

        Returns:
            The created finding. A credential can only belong to a technology, so
            the ones that would be discarded because no technology was discovered
            in the target are linked to a generic Git one instead.
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
        """Create the exposed repository and the secrets that it contains."""
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
        """Create a credential for a contributor of the repository.

        The caller decides which emails are worth creating, since this method
        creates a credential every time that it's called.

        Args:
            email: Email address of the contributor.
            name: Name of the contributor, which is kept in the context because it
              helps to identify who the email belongs to.
        """
        self.create_finding(
            Credential,
            email=email,
            context=f"/.git/ : Git contributor with name {name}" if name else "/.git/ : Git contributor",
        )
