from django.test import TestCase

from findings.enums import HostOS, Severity
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject
from tests.stats.test_base import BaseStatsAuthorizationTest

# pytype: disable=wrong-arg-types


class HostOSStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/host-os/"
    data = [
        SetupProject(
            hosts_fields=[
                {"os": os, "os_type": os_type}
                for os, os_type in [
                    ("Ubuntu 20.04 LTS", HostOS.LINUX),
                    ("CentOS 7", HostOS.LINUX),
                    ("RHEL 8", HostOS.LINUX),
                    ("Debian 11", HostOS.LINUX),
                    ("Windows Server 2019", HostOS.WINDOWS),
                    ("Windows Server 2022", HostOS.WINDOWS),
                    ("Windows 10 Pro", HostOS.WINDOWS),
                    ("FreeBSD 13", HostOS.FREEBSD),
                ]
            ]
            + [{"os": "OS discarded because it's fixed", "os_type": HostOS.LINUX, "is_fixed": True}],
        ),
        SetupProject(hosts_fields=[{"os": "macOS Big Sur", "os_type": HostOS.MACOS}]),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"os_type": HostOS.LINUX.value, "count": 4},
                {"os_type": HostOS.WINDOWS.value, "count": 3},
                {"os_type": HostOS.FREEBSD.value, "count": 1},
                {"os_type": HostOS.MACOS.value, "count": 1},
            ],
        ),
        ApiTestCase(["not_members"], expected=[]),
        ApiTestCase(
            ["members"],
            expected=[
                {"os_type": HostOS.LINUX.value, "count": 4},
                {"os_type": HostOS.WINDOWS.value, "count": 3},
                {"os_type": HostOS.FREEBSD.value, "count": 1},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[{"os_type": HostOS.MACOS.value, "count": 1}],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=2"),
        ApiTestCase(
            ["members"],
            expected=[
                {"os_type": HostOS.LINUX.value, "count": 4},
                {"os_type": HostOS.WINDOWS.value, "count": 3},
                {"os_type": HostOS.FREEBSD.value, "count": 1},
            ],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[{"os_type": HostOS.MACOS.value, "count": 1}],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=2"),
    ]


class HostVulnerabilitiesStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/host-vulnerabilities/"
    data = [
        SetupProject(
            vulnerabilities_fields=[
                {"severity": severity}
                for severity in (
                    [Severity.CRITICAL] * 2 + [Severity.HIGH] + [Severity.MEDIUM] * 5 + [Severity.LOW] * 10
                )
            ]
            + [
                {"severity": severity, "is_fixed": True}
                for severity in ([Severity.CRITICAL] + [Severity.MEDIUM] * 3 + [Severity.LOW] * 2)
            ]
        ),
        SetupProject(
            vulnerabilities_fields=[
                {"severity": severity}
                for severity in [Severity.CRITICAL] + [Severity.HIGH] * 3 + [Severity.MEDIUM] * 8 + [Severity.LOW] * 12
            ]
            + [
                {"severity": severity, "is_fixed": True}
                for severity in [Severity.HIGH] * 2 + [Severity.MEDIUM] * 5 + [Severity.LOW] * 10
            ]
        ),
        SetupProject(),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"id": 2, "open": 24, "fixed": 17, "critical": 1, "high": 3, "medium": 8, "low": 12, "info": 0},
                {"id": 1, "open": 18, "fixed": 6, "critical": 2, "high": 1, "medium": 5, "low": 10, "info": 0},
                {"id": 3, "open": 1, "fixed": 0, "critical": 0, "high": 0, "medium": 1, "low": 0, "info": 0},
            ],
        ),
        ApiTestCase(["not_members"], expected=[]),
        ApiTestCase(
            ["members"],
            expected=[{"id": 1, "open": 18, "fixed": 6, "critical": 2, "high": 1, "medium": 5, "low": 10, "info": 0}],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[{"id": 2, "open": 24, "fixed": 17, "critical": 1, "high": 3, "medium": 8, "low": 12, "info": 0}],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=2"),
    ]


class HostOSStatsAuthorizationTest(BaseStatsAuthorizationTest, TestCase):
    endpoint = "/api/stats/host-os/"
    project_1_members_expected = [{"os_type": HostOS.LINUX.value, "count": 1}]
    project_2_members_expected = [{"os_type": HostOS.WINDOWS.value, "count": 1}]


class HostVulnerabilitiesStatsAuthorizationTest(BaseStatsAuthorizationTest, TestCase):
    endpoint = "/api/stats/host-vulnerabilities/"
    project_1_members_expected = [
        {
            "id": 1,
            "ip": "10.10.10.10",
            "open": 1,
            "fixed": 0,
            "critical": 1,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
    ]
    project_2_members_expected = [
        {
            "id": 2,
            "ip": "10.10.10.20",
            "open": 1,
            "fixed": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 1,
            "info": 0,
        }
    ]
