from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class SshauditTest(ToolTest):
    tool_name = "SSH Audit"
    cases = [
        ToolTestCase(
            "libssh.json",
            [
                {"model": Technology, "name": "libssh", "version": "0.8.1"},
                {
                    "model": Vulnerability,
                    "name": "Insecure enc algorithm: chacha20-poly1305@openssh.com",
                    "description": "Vulnerable to the Terrapin attack (CVE-2023-48795), allowing message prefix truncation",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure enc algorithm: aes256-cbc",
                    "description": "Using weak cipher mode",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure enc algorithm: aes192-cbc",
                    "description": "Using weak cipher mode",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure enc algorithm: aes128-cbc",
                    "description": "Using weak cipher mode",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure enc algorithm: blowfish-cbc",
                    "description": "Using weak & deprecated Blowfish cipher\nUsing weak cipher mode\nUsing small 64-bit block size",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure enc algorithm: 3des-cbc",
                    "description": "Using broken & deprecated 3DES cipher\nUsing weak cipher mode\nUsing small 64-bit block size",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure kex algorithm: ecdh-sha2-nistp256",
                    "description": "Using elliptic curves that are suspected as being backdoored by the U.S. National Security Agency",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure kex algorithm: ecdh-sha2-nistp384",
                    "description": "Using elliptic curves that are suspected as being backdoored by the U.S. National Security Agency",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure kex algorithm: ecdh-sha2-nistp521",
                    "description": "Using elliptic curves that are suspected as being backdoored by the U.S. National Security Agency",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure kex algorithm: diffie-hellman-group14-sha1",
                    "description": "Using broken SHA-1 hash algorithm\n2048-bit modulus only provides 112-bits of symmetric strength",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure kex algorithm: diffie-hellman-group1-sha1",
                    "description": "Using small 1024-bit modulus\nVulnerable to the Logjam attack: https://en.wikipedia.org/wiki/Logjam_(computer_security)\nUsing broken SHA-1 hash algorithm",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure key algorithm: ssh-rsa",
                    "description": "Using broken SHA-1 hash algorithm\n2048-bit modulus only provides 112-bits of symmetric strength",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure mac algorithm: hmac-sha2-256",
                    "description": "Using encrypt-and-MAC mode",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure mac algorithm: hmac-sha2-512",
                    "description": "Using encrypt-and-MAC mode",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure mac algorithm: hmac-sha1",
                    "description": "Using broken SHA-1 hash algorithm\nUsing encrypt-and-MAC mode",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {"model": Vulnerability, "name": "CVE-2023-48795", "cve": "CVE-2023-48795"},
            ],
        )
    ]
