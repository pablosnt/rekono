from django.test import TestCase

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase


class SslscanTest(ParserTest, TestCase):
    tool_name = "Sslscan"
    cases = [
        ParserTestCase("empty.xml", []),
        ParserTestCase(
            "protocols.xml",
            [
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 supported",
                    "description": "Insecure TLS 1.0 supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.1"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.1 supported",
                    "description": "Insecure TLS 1.1 supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.2"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.2 cipher suite DES-CBC3-SHA supported",
                    "description": "TLS 1.2 DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.1 cipher suite DES-CBC3-SHA supported",
                    "description": "TLS 1.1 DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite DES-CBC3-SHA supported",
                    "description": "TLS 1.0 DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
            ],
        ),
        ParserTestCase(
            "heartbleed.xml",
            [
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 supported",
                    "description": "Insecure TLS 1.0 supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.1"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.1 supported",
                    "description": "Insecure TLS 1.1 supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.2"},
                {"model": Vulnerability, "name": "Heartbleed in TLS 1.1", "cve": "CVE-2014-0160"},
                {"model": Vulnerability, "name": "Heartbleed in TLS 1.0", "cve": "CVE-2014-0160"},
            ],
        ),
        ParserTestCase(
            "insecure-renegotiation.xml",
            [
                {"model": Technology, "name": "SSL", "version": "2"},
                {
                    "model": Vulnerability,
                    "name": "Insecure SSL 2 supported",
                    "description": "Insecure SSL 2 supported",
                    "severity": Severity.HIGH,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "SSL", "version": "3"},
                {
                    "model": Vulnerability,
                    "name": "Insecure SSL 3 supported",
                    "description": "Insecure SSL 3 supported",
                    "severity": Severity.HIGH,
                    "cwes": ["CWE-326"],
                },
                {"model": Technology, "name": "TLS", "version": "1.0"},
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 supported",
                    "description": "Insecure TLS 1.0 supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS renegotiation supported",
                    "description": "Insecure TLS renegotiation supported",
                    "severity": Severity.MEDIUM,
                    "cwes": ["CWE-264"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite DHE-RSA-DES-CBC3-SHA supported",
                    "description": "TLS 1.0 DHE-RSA-DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite RC4-SHA supported",
                    "description": "TLS 1.0 RC4-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite RC4-MD5 supported",
                    "description": "TLS 1.0 RC4-MD5 status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite DES-CBC3-SHA supported",
                    "description": "TLS 1.0 DES-CBC3-SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite TLS_RSA_EXPORT_WITH_RC4_40_MD5 supported",
                    "description": "TLS 1.0 TLS_RSA_EXPORT_WITH_RC4_40_MD5 status=accepted strength=weak",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite TLS_RSA_EXPORT_WITH_RC2_CBC_40_MD5 supported",
                    "description": "TLS 1.0 TLS_RSA_EXPORT_WITH_RC2_CBC_40_MD5 status=accepted strength=weak",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite TLS_RSA_EXPORT_WITH_DES40_CBC_SHA supported",
                    "description": "TLS 1.0 TLS_RSA_EXPORT_WITH_DES40_CBC_SHA status=accepted strength=weak",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite TLS_RSA_WITH_DES_CBC_SHA supported",
                    "description": "TLS 1.0 TLS_RSA_WITH_DES_CBC_SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite TLS_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA supported",
                    "description": "TLS 1.0 TLS_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA status=accepted strength=weak",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
                {
                    "model": Vulnerability,
                    "name": "Insecure TLS 1.0 cipher suite TLS_DHE_RSA_WITH_DES_CBC_SHA supported",
                    "description": "TLS 1.0 TLS_DHE_RSA_WITH_DES_CBC_SHA status=accepted strength=medium",
                    "severity": Severity.LOW,
                    "cwes": ["CWE-326"],
                },
            ],
        ),
    ]
