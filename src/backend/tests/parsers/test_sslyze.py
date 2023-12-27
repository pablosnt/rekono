from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class SslyzeTest(ToolTest):
    tool_name = "SSLyze"
    cases = [
        ToolTestCase(
            "protocols.json",
            [
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.0 is supported",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {"model": Technology, "name": "TLS", "version": "1.1"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.1 is supported",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {"model": Technology, "name": "TLS", "version": "1.2"},
                {"model": Technology, "name": "Generic TLS"},
                {
                    "model": Vulnerability,
                    "name": "Certificate subject error",
                    "description": "Certificate subject doesn't match hostname",
                    "severity": Severity.INFO,
                    "cwe": "CWE-295",
                },
            ],
        ),
        ToolTestCase(
            "vulnerabilities.json",
            [
                {"model": Technology, "name": "Generic TLS"},
                {"model": Vulnerability, "name": "Heartbleed", "cve": "CVE-2014-0160"},
                {
                    "model": Vulnerability,
                    "name": "OpenSSL CSS Injection",
                    "cve": "CVE-2014-0224",
                },
                {
                    "model": Vulnerability,
                    "name": "ROBOT",
                    "description": "Return Of the Bleichenbacher Oracle Threat",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-203",
                    "reference": "https://www.robotattack.org/",
                },
                {"model": Vulnerability, "name": "CRIME", "cve": "CVE-2012-4929"},
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.0 is supported",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {"model": Technology, "name": "TLS", "version": "1.1"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.1 is supported",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {"model": Technology, "name": "TLS", "version": "1.2"},
                {
                    "model": Vulnerability,
                    "name": "Certificate subject error",
                    "description": "Certificate subject doesn't match hostname",
                    "severity": Severity.INFO,
                    "cwe": "CWE-295",
                },
            ],
        ),
        ToolTestCase(
            "insecure-renegotiation.json",
            [
                {"model": Technology, "name": "Generic TLS"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS renegotiation supported",
                    "description": "Insecure TLS renegotiation supported",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-264",
                },
                {"model": Technology, "name": "SSL", "version": "3.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure SSL version supported",
                    "description": "SSL 3.0 is supported",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-326",
                },
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLS 1.0 TLS_RSA_WITH_RC4_128_SHA",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLS 1.0 TLS_RSA_WITH_RC4_128_MD5",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLS 1.0 TLS_RSA_EXPORT_WITH_RC4_40_MD5",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.0 is supported",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
            ],
        ),
    ]
