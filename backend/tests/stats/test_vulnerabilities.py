from django.test import TestCase

from findings.enums import Severity
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class VulnerabilityCVEStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/vulnerability-cve/"
    data = [
        SetupProject(
            vulnerabilities_fields=[
                {"cve": "CVE-2025-1001"},
                {"cve": "CVE-2025-1002"},
                {"cve": "CVE-2025-1003"},
                {"cve": "CVE-2025-1001", "is_fixed": True},
                {"cve": "CVE-2025-1002"},
                {"cve": None},
            ]
        ),
        SetupProject(vulnerabilities_fields=[{"cve": "CVE-2025-2001"}, {"cve": "CVE-2025-1001"}]),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"cve": "CVE-2025-1001", "open": 2, "fixed": 1},
                {"cve": "CVE-2025-1002", "open": 2, "fixed": 0},
                {"cve": "CVE-2025-1003", "open": 1, "fixed": 0},
                {"cve": "CVE-2025-2001", "open": 1, "fixed": 0},
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"cve": "CVE-2025-1002", "open": 2, "fixed": 0},
                {"cve": "CVE-2025-1001", "open": 1, "fixed": 1},
                {"cve": "CVE-2025-1003", "open": 1, "fixed": 0},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {"cve": "CVE-2025-1001", "open": 1, "fixed": 0},
                {"cve": "CVE-2025-2001", "open": 1, "fixed": 0},
            ],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
    ]


class VulnerabilityCWEStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/vulnerability-cwe/"
    data = [
        SetupProject(
            vulnerabilities_fields=[
                {"cwe": "CWE-200"},
                {"cwe": "CWE-79"},
                {"cwe": "CWE-89"},
                {"cwe": "CWE-200", "is_fixed": True},
                {"cwe": "CWE-79"},
                {"cwe": None},
            ]
        ),
        SetupProject(vulnerabilities_fields=[{"cwe": "CWE-22"}, {"cwe": "CWE-200"}]),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"cwe": "CWE-200", "open": 2, "fixed": 1},
                {"cwe": "CWE-79", "open": 2, "fixed": 0},
                {"cwe": "CWE-22", "open": 1, "fixed": 0},
                {"cwe": "CWE-89", "open": 1, "fixed": 0},
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"cwe": "CWE-79", "open": 2, "fixed": 0},
                {"cwe": "CWE-200", "open": 1, "fixed": 1},
                {"cwe": "CWE-89", "open": 1, "fixed": 0},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {"cwe": "CWE-200", "open": 1, "fixed": 0},
                {"cwe": "CWE-22", "open": 1, "fixed": 0},
            ],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
    ]


class VulnerabilityExploitCoverageStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/exploit-coverage/"
    data = [
        SetupProject(exploits_fields=[]),
        SetupProject(),
        SetupProject(
            vulnerabilities_fields=[{"is_fixed": True}],
            exploits_fields=[],
        ),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"has_exploits": False, "count": 1},
                {"has_exploits": True, "count": 1},
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[{"has_exploits": False, "count": 1}],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[{"has_exploits": True, "count": 1}],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=2"),
        ApiTestCase(["members"], endpoint="{endpoint}?project=3"),
        ApiTestCase(
            ["members"],
            expected=[{"has_exploits": False, "count": 1}],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[{"has_exploits": True, "count": 1}],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["members"], endpoint="{endpoint}?target=3"),
    ]


class VulnerabilityStatusPerSeverityStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/vulnerability-status/"
    data = [
        SetupProject(
            vulnerabilities_fields=[
                {"severity": Severity.CRITICAL},
                {"severity": Severity.CRITICAL, "is_fixed": True},
                {"severity": Severity.HIGH},
                {"severity": Severity.HIGH, "is_fixed": True},
                {"severity": Severity.HIGH, "is_fixed": True},
                {"severity": Severity.MEDIUM},
                {"severity": Severity.MEDIUM},
                {"severity": Severity.LOW, "is_fixed": True},
                {"severity": Severity.INFO},
            ]
        ),
        SetupProject(
            vulnerabilities_fields=[
                {"severity": Severity.CRITICAL, "is_fixed": True},
                {"severity": Severity.HIGH},
                {"severity": Severity.MEDIUM, "is_fixed": True},
            ]
        ),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"severity": Severity.CRITICAL.name.capitalize(), "open": 1, "fixed": 2},
                {"severity": Severity.HIGH.name.capitalize(), "open": 2, "fixed": 2},
                {"severity": Severity.MEDIUM.name.capitalize(), "open": 2, "fixed": 1},
                {"severity": Severity.LOW.name.capitalize(), "open": 0, "fixed": 1},
                {"severity": Severity.INFO.name.capitalize(), "open": 1, "fixed": 0},
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"severity": Severity.CRITICAL.name.capitalize(), "open": 1, "fixed": 1},
                {"severity": Severity.HIGH.name.capitalize(), "open": 1, "fixed": 2},
                {"severity": Severity.MEDIUM.name.capitalize(), "open": 2, "fixed": 0},
                {"severity": Severity.LOW.name.capitalize(), "open": 0, "fixed": 1},
                {"severity": Severity.INFO.name.capitalize(), "open": 1, "fixed": 0},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {"severity": Severity.CRITICAL.name.capitalize(), "open": 0, "fixed": 1},
                {"severity": Severity.HIGH.name.capitalize(), "open": 1, "fixed": 0},
                {"severity": Severity.MEDIUM.name.capitalize(), "open": 0, "fixed": 1},
            ],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
    ]
