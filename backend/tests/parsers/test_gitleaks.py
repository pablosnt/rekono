from pathlib import Path as PathFile

from django.test import TestCase

from findings.enums import PathType, Severity
from findings.models import Credential, Path, Vulnerability
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase


class GitleaksTest(ParserTest, TestCase):
    tool_name = "GitLeaks"
    cases = [
        ParserTestCase("empty.json", []),
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
            # Simulate a dumped repository so the parser processes the report. The execution directory
            # points to a non-existent path so no real git history is harvested during the test.
            executor_attributes={
                "git_directory_dumped": True,
                "execution_directory": PathFile("/nonexistent-rekono-gitleaks-test"),
            },
        ),
    ]
