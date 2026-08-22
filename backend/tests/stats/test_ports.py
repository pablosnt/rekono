from django.test import TestCase

from findings.enums import TransportProtocol
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject
from tests.stats.test_base import BaseStatsAuthorizationTest

# pytype: disable=wrong-arg-types


class PortStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/port/"
    data = [
        SetupProject(
            ports_fields=[
                {"port": 80, "service": "http", "protocol": TransportProtocol.TCP},
                {"port": 443, "service": "https", "protocol": TransportProtocol.TCP},
                {"port": 22, "service": "ssh", "protocol": TransportProtocol.TCP},
                {"port": 80, "service": "http", "protocol": TransportProtocol.TCP},
                {"port": 53, "service": "dns", "protocol": TransportProtocol.UDP},
                {"port": 80, "service": "http", "protocol": TransportProtocol.TCP, "is_fixed": True},
            ]
        ),
        SetupProject(
            ports_fields=[
                {"port": 443, "service": "https", "protocol": TransportProtocol.TCP},
                {"port": 21, "service": "ftp", "protocol": TransportProtocol.TCP},
                {"port": 3306, "service": "mysql", "protocol": TransportProtocol.TCP},
            ]
        ),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "http", "port": 80, "protocol": TransportProtocol.TCP.value, "count": 2},
                {"service": "https", "port": 443, "protocol": TransportProtocol.TCP.value, "count": 2},
                {"service": "dns", "port": 53, "protocol": TransportProtocol.UDP.value, "count": 1},
                {"service": "ftp", "port": 21, "protocol": TransportProtocol.TCP.value, "count": 1},
                {"service": "mysql", "port": 3306, "protocol": TransportProtocol.TCP.value, "count": 1},
                {"service": "ssh", "port": 22, "protocol": TransportProtocol.TCP.value, "count": 1},
            ],
        ),
        ApiTestCase(["not_members"], expected=[]),
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "http", "port": 80, "protocol": TransportProtocol.TCP.value, "count": 2},
                {"service": "dns", "port": 53, "protocol": TransportProtocol.UDP.value, "count": 1},
                {"service": "https", "port": 443, "protocol": TransportProtocol.TCP.value, "count": 1},
                {"service": "ssh", "port": 22, "protocol": TransportProtocol.TCP.value, "count": 1},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "ftp", "port": 21, "protocol": TransportProtocol.TCP.value, "count": 1},
                {"service": "https", "port": 443, "protocol": TransportProtocol.TCP.value, "count": 1},
                {"service": "mysql", "port": 3306, "protocol": TransportProtocol.TCP.value, "count": 1},
            ],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=2"),
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "http", "port": 80, "protocol": TransportProtocol.TCP.value, "count": 2},
                {"service": "dns", "port": 53, "protocol": TransportProtocol.UDP.value, "count": 1},
                {"service": "https", "port": 443, "protocol": TransportProtocol.TCP.value, "count": 1},
                {"service": "ssh", "port": 22, "protocol": TransportProtocol.TCP.value, "count": 1},
            ],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "ftp", "port": 21, "protocol": TransportProtocol.TCP.value, "count": 1},
                {"service": "https", "port": 443, "protocol": TransportProtocol.TCP.value, "count": 1},
                {"service": "mysql", "port": 3306, "protocol": TransportProtocol.TCP.value, "count": 1},
            ],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=2"),
    ]


class PortStatsAuthorizationTest(BaseStatsAuthorizationTest, TestCase):
    endpoint = "/api/stats/port/"
    project_1_members_expected = [{"service": "http", "port": 80, "protocol": TransportProtocol.TCP.value, "count": 1}]
    project_2_members_expected = [
        {"service": "https", "port": 443, "protocol": TransportProtocol.TCP.value, "count": 1}
    ]
