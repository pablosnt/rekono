from datetime import date, timedelta

from findings.enums import Severity, TriageStatus
from tests.framework import StatsTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class LatestVulnerabilitiesTest(StatsTest):
    endpoint = "/api/stats/latest-vulnerabilities/"
    data = [
        SetupProject(1, 6),
        SetupProject(vulnerabilities_fields=[{"is_fixed": True}, {"triage_status": TriageStatus.FALSE_POSITIVE}]),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"id": value, "is_fixed": False, "triage_status": TriageStatus.UNTRIAGED.value} for value in range(1, 6)
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"id": value, "is_fixed": False, "triage_status": TriageStatus.UNTRIAGED.value} for value in range(1, 6)
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["members", "not_members"], endpoint="{endpoint}?project=2"),
        ApiTestCase(
            ["members"],
            expected=[
                {"id": value, "is_fixed": False, "triage_status": TriageStatus.UNTRIAGED.value} for value in range(1, 6)
            ],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(["members", "not_members"], endpoint="{endpoint}?target=2"),
    ]


class VulnerabilityTrendingStatsTest(StatsTest):
    endpoint = "/api/stats/vulnerability-trending/"
    data = [
        SetupProject(
            vulnerabilities_fields=[
                {"cve": "CVE-2025-1001", "trending": True, "severity": Severity.CRITICAL},
                {"cve": "CVE-2025-1002", "trending": True, "severity": Severity.HIGH},
                {"cve": "CVE-2025-1003", "trending": False, "severity": Severity.MEDIUM},
                {"cve": "CVE-2025-1001", "trending": True, "severity": Severity.CRITICAL, "is_fixed": True},
                {"cve": None, "severity": Severity.HIGH},
            ]
        ),
        SetupProject(
            vulnerabilities_fields=[
                {"cve": "CVE-2025-2001", "trending": True, "severity": Severity.HIGH},
                {"cve": "CVE-2025-1001", "trending": True, "severity": Severity.CRITICAL},
            ]
        ),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"cve": "CVE-2025-1001", "severity_value": Severity.CRITICAL.name.capitalize(), "open": 2, "fixed": 1},
                {"cve": "CVE-2025-1002", "severity_value": Severity.HIGH.name.capitalize(), "open": 1, "fixed": 0},
                {"cve": "CVE-2025-2001", "severity_value": Severity.HIGH.name.capitalize(), "open": 1, "fixed": 0},
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"cve": "CVE-2025-1001", "severity_value": Severity.CRITICAL.name.capitalize(), "open": 1, "fixed": 1},
                {"cve": "CVE-2025-1002", "severity_value": Severity.HIGH.name.capitalize(), "open": 1, "fixed": 0},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {"cve": "CVE-2025-1001", "severity_value": Severity.CRITICAL.name.capitalize(), "open": 1, "fixed": 0},
                {"cve": "CVE-2025-2001", "severity_value": Severity.HIGH.name.capitalize(), "open": 1, "fixed": 0},
            ],
            endpoint="{endpoint}?target=2",
        ),
    ]


class VulnerabilityCVEStatsTest(StatsTest):
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


class VulnerabilityCWEStatsTest(StatsTest):
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


class VulnerabilitySeverityStatsTest(StatsTest):
    endpoint = "/api/stats/vulnerability-severity/"
    data = [
        SetupProject(
            vulnerabilities_fields=[
                {"severity": Severity.CRITICAL},
                {"severity": Severity.HIGH},
                {"severity": Severity.MEDIUM},
                {"severity": Severity.LOW},
                {"severity": Severity.INFO},
                {"severity": Severity.CRITICAL, "is_fixed": True},
                {"severity": Severity.HIGH, "is_fixed": True},
                {"severity": Severity.MEDIUM, "is_fixed": True},
            ]
        ),
        SetupProject(
            vulnerabilities_fields=[
                {"severity": Severity.CRITICAL},
                {"severity": Severity.HIGH},
                {"severity": Severity.HIGH},
                {"severity": Severity.MEDIUM},
                {"severity": Severity.MEDIUM},
                {"severity": Severity.LOW, "is_fixed": True},
            ]
        ),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"severity": Severity.CRITICAL.name.capitalize(), "open": 2, "fixed": 1},
                {"severity": Severity.HIGH.name.capitalize(), "open": 3, "fixed": 1},
                {"severity": Severity.MEDIUM.name.capitalize(), "open": 3, "fixed": 1},
                {"severity": Severity.LOW.name.capitalize(), "open": 1, "fixed": 1},
                {"severity": Severity.INFO.name.capitalize(), "open": 1, "fixed": 0},
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"severity": Severity.CRITICAL.name.capitalize(), "open": 1, "fixed": 1},
                {"severity": Severity.HIGH.name.capitalize(), "open": 1, "fixed": 1},
                {"severity": Severity.MEDIUM.name.capitalize(), "open": 1, "fixed": 1},
                {"severity": Severity.LOW.name.capitalize(), "open": 1, "fixed": 0},
                {"severity": Severity.INFO.name.capitalize(), "open": 1, "fixed": 0},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {"severity": Severity.CRITICAL.name.capitalize(), "open": 1, "fixed": 0},
                {"severity": Severity.HIGH.name.capitalize(), "open": 2, "fixed": 0},
                {"severity": Severity.MEDIUM.name.capitalize(), "open": 2, "fixed": 0},
                {"severity": Severity.LOW.name.capitalize(), "open": 0, "fixed": 1},
            ],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
    ]


class VulnerabilityStatusStatsTest(StatsTest):
    endpoint = "/api/stats/vulnerability-status/"
    data = [
        SetupProject(
            vulnerabilities_fields=[
                {"severity": Severity.CRITICAL},
                {"severity": Severity.HIGH},
                {"severity": Severity.MEDIUM, "is_fixed": True},
                {"severity": Severity.LOW, "is_fixed": True},
                {"severity": Severity.INFO, "is_fixed": True},
            ]
        ),
        SetupProject(
            vulnerabilities_fields=[
                {"severity": Severity.CRITICAL},
                {"severity": Severity.HIGH, "is_fixed": True},
                {"severity": Severity.MEDIUM, "is_fixed": True},
            ]
        ),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(["members"], expected=[{"is_fixed": False, "count": 3}, {"is_fixed": True, "count": 5}]),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[{"is_fixed": False, "count": 2}, {"is_fixed": True, "count": 3}],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[{"is_fixed": False, "count": 1}, {"is_fixed": True, "count": 2}],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
    ]


class VulnerabilityStatusPerSeverityStatsTest(StatsTest):
    endpoint = "/api/stats/vulnerability-status-per-severity/"
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


class VulnerabilityEvolutionStatsTest(StatsTest):
    endpoint = "/api/stats/vulnerability-evolution/"
    data = [
        SetupProject(
            3,
            vulnerabilities_fields=[
                {"severity": Severity.CRITICAL},
                {"severity": Severity.MEDIUM},
                {"severity": Severity.MEDIUM},
            ],
        ),
        SetupProject(2, vulnerabilities_fields=[{"severity": Severity.LOW}, {"severity": Severity.LOW}]),
        SetupProject(vulnerabilities_fields=[{"severity": Severity.HIGH}]),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "date": str(date.today() - timedelta(days=11)),
                    "severity": Severity.CRITICAL.name.capitalize(),
                    "count": 1,
                },
                {
                    "date": str(date.today() - timedelta(days=11)),
                    "severity": Severity.MEDIUM.name.capitalize(),
                    "count": 2,
                },
                {
                    "date": str(date.today() - timedelta(days=12)),
                    "severity": Severity.CRITICAL.name.capitalize(),
                    "count": 1,
                },
                {
                    "date": str(date.today() - timedelta(days=12)),
                    "severity": Severity.MEDIUM.name.capitalize(),
                    "count": 2,
                },
                {
                    "date": str(date.today() - timedelta(days=13)),
                    "severity": Severity.CRITICAL.name.capitalize(),
                    "count": 1,
                },
                {
                    "date": str(date.today() - timedelta(days=13)),
                    "severity": Severity.MEDIUM.name.capitalize(),
                    "count": 2,
                },
                {
                    "date": str(date.today() - timedelta(days=21)),
                    "severity": Severity.LOW.name.capitalize(),
                    "count": 2,
                },
                {
                    "date": str(date.today() - timedelta(days=22)),
                    "severity": Severity.LOW.name.capitalize(),
                    "count": 2,
                },
                {
                    "date": str(date.today() - timedelta(days=31)),
                    "severity": Severity.HIGH.name.capitalize(),
                    "count": 1,
                },
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "date": str(date.today() - timedelta(days=11)),
                    "severity": Severity.CRITICAL.name.capitalize(),
                    "count": 1,
                },
                {
                    "date": str(date.today() - timedelta(days=11)),
                    "severity": Severity.MEDIUM.name.capitalize(),
                    "count": 2,
                },
                {
                    "date": str(date.today() - timedelta(days=12)),
                    "severity": Severity.CRITICAL.name.capitalize(),
                    "count": 1,
                },
                {
                    "date": str(date.today() - timedelta(days=12)),
                    "severity": Severity.MEDIUM.name.capitalize(),
                    "count": 2,
                },
                {
                    "date": str(date.today() - timedelta(days=13)),
                    "severity": Severity.CRITICAL.name.capitalize(),
                    "count": 1,
                },
                {
                    "date": str(date.today() - timedelta(days=13)),
                    "severity": Severity.MEDIUM.name.capitalize(),
                    "count": 2,
                },
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "date": str(date.today() - timedelta(days=21)),
                    "severity": Severity.LOW.name.capitalize(),
                    "count": 2,
                },
                {
                    "date": str(date.today() - timedelta(days=22)),
                    "severity": Severity.LOW.name.capitalize(),
                    "count": 2,
                },
            ],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "date": str(date.today() - timedelta(days=11)),
                    "severity": Severity.CRITICAL.name.capitalize(),
                    "count": 1,
                },
                {
                    "date": str(date.today() - timedelta(days=11)),
                    "severity": Severity.MEDIUM.name.capitalize(),
                    "count": 2,
                },
            ],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "date": str(date.today() - timedelta(days=12)),
                    "severity": Severity.CRITICAL.name.capitalize(),
                    "count": 1,
                },
                {
                    "date": str(date.today() - timedelta(days=12)),
                    "severity": Severity.MEDIUM.name.capitalize(),
                    "count": 2,
                },
            ],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?target=1"),
    ]
