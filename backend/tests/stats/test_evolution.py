from django.test import TestCase

from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class MonthlyEvolutionBaseTest(ApiTest):
    """Base test for all monthly evolution viewsets.

    Two projects are created, each containing one finding of every type
    (OSINT, Host, Port, Path, Technology, Credential, Vulnerability, Exploit)
    linked to an execution with a concrete start date. Every evolution viewset
    queries only its own model, so each project contributes exactly one
    discoverable finding regardless of which subclass endpoint is tested.

    Subclasses must only override `endpoint`.
    """

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
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[{"discovered": 1, "fixed": 0, "active": 1}],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[{"discovered": 1, "fixed": 0, "active": 1}],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=2"),
        ApiTestCase(
            ["members"],
            expected=[{"discovered": 1, "fixed": 0, "active": 1}],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[{"discovered": 1, "fixed": 0, "active": 1}],
            endpoint="{endpoint}?target=2",
        ),
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
