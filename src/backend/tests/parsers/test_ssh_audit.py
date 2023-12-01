from findings.models import Technology, Vulnerability
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class SshauditTest(ToolTest):
    tool_name = "SSH Audit"
    cases = [
        ToolTestCase(
            "cve_2018_10933.txt",
            [
                {"model": Technology, "name": "libssh", "version": "0.8.1"},
                {
                    "model": Vulnerability,
                    "name": "Authentication bypass",
                    "cve": "CVE-2018-10933",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure key exchange algorithms",
                    "description": "ecdh-sha2-nistp256, ecdh-sha2-nistp384, ecdh-sha2-nistp521, diffie-hellman-group1-sha1",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure host key algorithms",
                    "description": "ssh-rsa",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure encryption algorithms",
                    "description": "aes256-cbc, aes192-cbc, aes128-cbc, blowfish-cbc, 3des-cbc",
                },
            ],
        ),
        ToolTestCase(
            "cve_2018_15473.txt",
            [
                {"model": Technology, "name": "OpenSSH", "version": "7.7"},
                {
                    "model": Vulnerability,
                    "name": "Enumerate usernames due to timing discrepencies",
                    "cve": "CVE-2018-15473",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure key exchange algorithms",
                    "description": "ecdh-sha2-nistp256, ecdh-sha2-nistp384, ecdh-sha2-nistp521",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure host key algorithms",
                    "description": "ssh-rsa, ecdsa-sha2-nistp256",
                },
            ],
        ),
    ]
