from django.test import TestCase

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase


class SslyzeTest(ParserTest, TestCase):
    tool_name = "SSLyze"
    cases = [
        ParserTestCase(
            "protocols.json",
            [
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.0 is supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.1"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.1 is supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.2"},
                {"model": Technology, "name": "Generic TLS"},
                {
                    "model": Vulnerability,
                    "name": "Certificate validation error",
                    "description": "The certificate is not valid for the scanned host",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-295"],
                },
            ],
        ),
        ParserTestCase(
            "vulnerabilities.json",
            [
                {"model": Technology, "name": "Generic TLS"},
                {"model": Vulnerability, "name": "Heartbleed", "cve": "CVE-2014-0160"},
                {"model": Vulnerability, "name": "OpenSSL CSS Injection", "cve": "CVE-2014-0224"},
                {
                    "model": Vulnerability,
                    "name": "ROBOT",
                    "description": "Return Of the Bleichenbacher Oracle Threat",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-203"],
                    "reference": "https://www.robotattack.org/",
                },
                {"model": Vulnerability, "name": "CRIME", "cve": "CVE-2012-4929"},
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.0 is supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.1"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.1 is supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.2"},
            ],
        ),
        ParserTestCase(
            "certificate-valid.json",
            [
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.0 is supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.1"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.1 is supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.2"},
                {"model": Technology, "name": "TLS", "version": "1.3"},
            ],
        ),
        ParserTestCase(
            "insecure-renegotiation.json",
            [
                {"model": Technology, "name": "Generic TLS"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS renegotiation supported",
                    "description": "Insecure TLS renegotiation supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-264"],
                },
                {"model": Technology, "name": "SSL", "version": "3.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure SSL version supported",
                    "description": "SSL 3.0 is supported",
                    "severity": Severity.HIGH,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLS 1.0 TLS_RSA_WITH_RC4_128_SHA",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLS 1.0 TLS_RSA_WITH_RC4_128_MD5",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure cipher suite supported",
                    "description": "TLS 1.0 TLS_RSA_EXPORT_WITH_RC4_40_MD5",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS version supported",
                    "description": "TLS 1.0 is supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Certificate validation error",
                    "description": "The certificate is not valid for the scanned host",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-295"],
                },
            ],
        ),
    ]
