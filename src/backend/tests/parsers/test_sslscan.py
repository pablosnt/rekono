from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class SslscanTest(ToolTest):
    tool_name = "Sslscan"
    cases = [
        ToolTestCase(
            "protocols.xml",
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
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.2 DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.1 DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
            ],
        ),
        ToolTestCase(
            "heartbleed.xml",
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
                {
                    "model": Vulnerability,
                    "name": "Heartbleed in TLSv1.1",
                    "cve": "CVE-2014-0160",
                },
                {
                    "model": Vulnerability,
                    "name": "Heartbleed in TLSv1.0",
                    "cve": "CVE-2014-0160",
                },
            ],
        ),
        ToolTestCase(
            "insecure-renegotiation.xml",
            [
                {"model": Technology, "name": "SSL", "version": "2"},
                {
                    "model": Vulnerability,
                    "name": "Insecure SSL version supported",
                    "description": "SSL 2 is supported",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-326",
                },
                {"model": Technology, "name": "SSL", "version": "3"},
                {
                    "model": Vulnerability,
                    "name": "Insecure SSL version supported",
                    "description": "SSL 3 is supported",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-326",
                },
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.0 is supported",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS renegotiation supported",
                    "description": "Insecure TLS renegotiation supported",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-264",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 DHE-RSA-DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 RC4-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 RC4-MD5 status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 TLS_RSA_EXPORT_WITH_RC4_40_MD5 status=accepted strength=weak",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 TLS_RSA_EXPORT_WITH_RC2_CBC_40_MD5 status=accepted strength=weak",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 TLS_RSA_EXPORT_WITH_DES40_CBC_SHA status=accepted strength=weak",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 TLS_RSA_WITH_DES_CBC_SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 TLS_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA status=accepted strength=weak",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLSv1.0 TLS_DHE_RSA_WITH_DES_CBC_SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwe": "CWE-326",
                },
            ],
        ),
    ]
