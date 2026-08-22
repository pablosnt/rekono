from django.test import TestCase

from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject
from tests.stats.test_base import BaseStatsAuthorizationTest

# pytype: disable=wrong-arg-types


class MonthlyEvolutionBaseTest(ApiTest):
    data = [
        SetupProject(
            osint_fields=[{}],
            hosts_fields=[{}],
            ports_fields=[{}],
            paths_fields=[{}],
            technologies_fields=[{}],
            credentials_fields=[{}],
            vulnerabilities_fields=[{}],
            exploits_fields=[{}],
        ),
        SetupProject(
            osint_fields=[{}],
            hosts_fields=[{}],
            ports_fields=[{}],
            paths_fields=[{}],
            technologies_fields=[{}],
            credentials_fields=[{}],
            vulnerabilities_fields=[{}],
            exploits_fields=[{}],
        ),
    ]
    cases = [
        ApiTestCase(["members"]),
        ApiTestCase(["not_members"], expected=[]),
        ApiTestCase(
            ["members"],
            expected=[{"discovered": 1, "fixed": 0, "active": 1}],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[{"discovered": 1, "fixed": 0, "active": 1}],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=2"),
        ApiTestCase(
            ["members"],
            expected=[{"discovered": 1, "fixed": 0, "active": 1}],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[{"discovered": 1, "fixed": 0, "active": 1}],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=2"),
    ]


class OSINTEvolutionTest(MonthlyEvolutionBaseTest, TestCase):
    endpoint = "/api/stats/osint-evolution/"


class HostEvolutionTest(MonthlyEvolutionBaseTest, TestCase):
    endpoint = "/api/stats/host-evolution/"


class PortEvolutionTest(MonthlyEvolutionBaseTest, TestCase):
    endpoint = "/api/stats/port-evolution/"


class PathEvolutionTest(MonthlyEvolutionBaseTest, TestCase):
    endpoint = "/api/stats/path-evolution/"


class TechnologyEvolutionTest(MonthlyEvolutionBaseTest, TestCase):
    endpoint = "/api/stats/technology-evolution/"


class CredentialEvolutionTest(MonthlyEvolutionBaseTest, TestCase):
    endpoint = "/api/stats/credential-evolution/"


class VulnerabilityEvolutionTest(MonthlyEvolutionBaseTest, TestCase):
    endpoint = "/api/stats/vulnerability-evolution/"


class ExploitEvolutionTest(MonthlyEvolutionBaseTest, TestCase):
    endpoint = "/api/stats/exploit-evolution/"


class MonthlyEvolutionAuthorizationBaseTest(BaseStatsAuthorizationTest):
    """Base authorization test for all monthly evolution viewsets.

    Both projects report the same values, because each one contains exactly one finding
    of every type, discovered in the current month and not fixed. So any finding leaked
    from the other project is reported as a second discovered finding.

    Subclasses must only override `endpoint`.
    """

    project_1_members_expected = [{"discovered": 1, "fixed": 0, "active": 1}]
    project_2_members_expected = [{"discovered": 1, "fixed": 0, "active": 1}]


class OSINTEvolutionAuthorizationTest(MonthlyEvolutionAuthorizationBaseTest, TestCase):
    endpoint = "/api/stats/osint-evolution/"


class HostEvolutionAuthorizationTest(MonthlyEvolutionAuthorizationBaseTest, TestCase):
    endpoint = "/api/stats/host-evolution/"


class PortEvolutionAuthorizationTest(MonthlyEvolutionAuthorizationBaseTest, TestCase):
    endpoint = "/api/stats/port-evolution/"


class PathEvolutionAuthorizationTest(MonthlyEvolutionAuthorizationBaseTest, TestCase):
    endpoint = "/api/stats/path-evolution/"


class TechnologyEvolutionAuthorizationTest(MonthlyEvolutionAuthorizationBaseTest, TestCase):
    endpoint = "/api/stats/technology-evolution/"


class CredentialEvolutionAuthorizationTest(MonthlyEvolutionAuthorizationBaseTest, TestCase):
    endpoint = "/api/stats/credential-evolution/"


class VulnerabilityEvolutionAuthorizationTest(MonthlyEvolutionAuthorizationBaseTest, TestCase):
    endpoint = "/api/stats/vulnerability-evolution/"


class ExploitEvolutionAuthorizationTest(MonthlyEvolutionAuthorizationBaseTest, TestCase):
    endpoint = "/api/stats/exploit-evolution/"
