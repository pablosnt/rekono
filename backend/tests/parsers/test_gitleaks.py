import os
import shutil
import subprocess
import tempfile
from pathlib import Path as PathFile
from unittest.mock import patch

from django.test import TestCase

from findings.enums import PathType, Severity
from findings.models import Credential, Path, Technology, Vulnerability
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase
from tools.parsers.base import BaseParser


class GitleaksTest(ParserTest, TestCase):
    tool_name = "GitLeaks"
    cases = [
        ParserTestCase("empty.json", []),
        ParserTestCase(
            "not-a-list.json",
            [
                {"model": Path, "path": "/.git", "type": PathType.ENDPOINT},
                {"model": Vulnerability, "name": "Exposed git repository", "severity": Severity.HIGH},
            ],
            executor_attributes={
                "git_directory_dumped": True,
                "execution_directory": PathFile("/nonexistent-rekono-gitleaks-test"),
            },
        ),
        ParserTestCase(
            "leaky-repo.json",
            [
                {"model": Path, "path": "/.git", "type": PathType.ENDPOINT},
                {"model": Vulnerability, "name": "Exposed git repository", "severity": Severity.HIGH},
                {
                    "model": Credential,
                    "secret": 'token: "7f9cc25de23d1a255720b0ae4551f4044d600f46"',
                    "context": "/.git/ : hub -> Line 4",
                },
                {
                    "model": Credential,
                    "email": "git@asdf.com",
                    "context": "/.git/ : Git contributor with name ASDF",
                },
                {"model": Credential, "secret": "xoxp-858723095049", "context": "/.git/ : .bash_profile -> Line 23"},
                {
                    "model": Credential,
                    "secret": "API_TOKEN='51e61afee2c2667123fc9ed160a0a20b330c8f74'",
                    "context": "/.git/ : .bash_profile -> Line 22",
                },
                {
                    "model": Credential,
                    "secret": 'API_KEY="38c47f19e349153fa963bb3b3212fe8e-us11"',
                    "context": "/.git/ : .bashrc -> Line 106",
                },
                {
                    "model": Credential,
                    "secret": 'TOKEN="c77e01c1e89682e4d4b94a059a7fd2b37ab326ed"',
                    "context": "/.git/ : .bashrc -> Line 109",
                },
                {
                    "model": Credential,
                    "secret": "-----BEGIN RSA PRIVATE KEY-----",
                    "context": "/.git/ : .ssh/id_rsa -> Line 1",
                },
                {
                    "model": Credential,
                    "secret": "-----BEGIN PRIVATE KEY-----",
                    "context": "/.git/ : misc-keys/cert-key.pem -> Line 1",
                },
            ],
            executor_attributes={
                "git_directory_dumped": True,
                "execution_directory": PathFile("/nonexistent-rekono-gitleaks-test"),
            },
        ),
    ]

    def _run_parser(self, report_name: str, executor_attributes: dict) -> "object":
        executor = self.execution.configuration.tool.executor_class(self.execution)
        for attribute, value in executor_attributes.items():
            setattr(executor, attribute, value)
        executor.report = self.data_dir / "reports" / "gitleaks" / report_name
        parser = self.execution.configuration.tool.parser_class(executor, None)
        parser.findings = []
        parser.parse()
        return parser

    def test_git_history_harvesting(self) -> None:
        repository = PathFile(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, repository, ignore_errors=True)
        subprocess.run(["git", "init", "-q"], cwd=repository)

        def commit(author_email: str, author_name: str, committer_email: str, committer_name: str) -> None:
            subprocess.run(
                ["git", "commit", "--allow-empty", "-q", "-m", "commit"],
                cwd=repository,
                env={
                    **os.environ,
                    "GIT_AUTHOR_EMAIL": author_email,
                    "GIT_AUTHOR_NAME": author_name,
                    "GIT_COMMITTER_EMAIL": committer_email,
                    "GIT_COMMITTER_NAME": committer_name,
                },
            )

        alice = "alice@example.com"
        bob = "bob@example.com"
        carol = "carol@example.com"
        commit(alice, "Alice", alice, "Alice")
        commit(bob, "Bob", carol, "Carol")
        parser = self._run_parser(
            "single-secret.json", {"git_directory_dumped": True, "execution_directory": repository}
        )
        credentials = [finding for finding in parser.findings if isinstance(finding, Credential)]
        self.assertEqual({alice, bob, carol}, {e.email for e in credentials if e.email})

    @patch("tools.parsers.gitleaks.subprocess.run", side_effect=OSError("git is not available"))
    def test_git_history_harvesting_error(self, run_mock: object) -> None:
        repository = PathFile(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, repository, ignore_errors=True)
        parser = self._run_parser(
            "single-secret.json",
            {"git_directory_dumped": True, "execution_directory": repository},
        )
        credentials = [finding for finding in parser.findings if isinstance(finding, Credential)]
        self.assertEqual(1, len(credentials))

    def test_orphan_credential_falls_back_to_git_technology(self) -> None:
        executor = self.execution.configuration.tool.executor_class(self.execution)
        parser = self.execution.configuration.tool.parser_class(executor, None)
        git_technology = Technology(name="Git")
        retried_credential = Credential(secret="orphan-secret")
        with patch.object(
            BaseParser, "create_finding", side_effect=[None, git_technology, retried_credential]
        ) as base_mock:
            result = parser.create_finding(Credential, secret=retried_credential.secret)
        self.assertEqual(retried_credential, result)
        self.assertEqual(git_technology, parser.git_technology)
        # Base parser called three times: discarded credential, generic Git technology, retried credential with git technology
        self.assertEqual(3, base_mock.call_count)
