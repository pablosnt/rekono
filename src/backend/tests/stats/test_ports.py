from django.test import TestCase

from findings.enums import Protocol
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class PortStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/port/"
    data = [
        SetupProject(
            ports_fields=[
                {"port": 80, "service": "http", "protocol": Protocol.TCP},
                {"port": 443, "service": "https", "protocol": Protocol.TCP},
                {"port": 22, "service": "ssh", "protocol": Protocol.TCP},
                {"port": 80, "service": "http", "protocol": Protocol.TCP},
                {"port": 53, "service": "dns", "protocol": Protocol.UDP},
                {"port": 80, "service": "http", "protocol": Protocol.TCP, "is_fixed": True},
            ]
        ),
        SetupProject(
            ports_fields=[
                {"port": 443, "service": "https", "protocol": Protocol.TCP},
                {"port": 21, "service": "ftp", "protocol": Protocol.TCP},
                {"port": 3306, "service": "mysql", "protocol": Protocol.TCP},
            ]
        ),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "http", "port": 80, "protocol": Protocol.TCP.value, "count": 2},
                {"service": "https", "port": 443, "protocol": Protocol.TCP.value, "count": 2},
                {"service": "dns", "port": 53, "protocol": Protocol.UDP.value, "count": 1},
                {"service": "ftp", "port": 21, "protocol": Protocol.TCP.value, "count": 1},
                {"service": "mysql", "port": 3306, "protocol": Protocol.TCP.value, "count": 1},
                {"service": "ssh", "port": 22, "protocol": Protocol.TCP.value, "count": 1},
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "http", "port": 80, "protocol": Protocol.TCP.value, "count": 2},
                {"service": "dns", "port": 53, "protocol": Protocol.UDP.value, "count": 1},
                {"service": "https", "port": 443, "protocol": Protocol.TCP.value, "count": 1},
                {"service": "ssh", "port": 22, "protocol": Protocol.TCP.value, "count": 1},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "ftp", "port": 21, "protocol": Protocol.TCP.value, "count": 1},
                {"service": "https", "port": 443, "protocol": Protocol.TCP.value, "count": 1},
                {"service": "mysql", "port": 3306, "protocol": Protocol.TCP.value, "count": 1},
            ],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "http", "port": 80, "protocol": Protocol.TCP.value, "count": 2},
                {"service": "dns", "port": 53, "protocol": Protocol.UDP.value, "count": 1},
                {"service": "https", "port": 443, "protocol": Protocol.TCP.value, "count": 1},
                {"service": "ssh", "port": 22, "protocol": Protocol.TCP.value, "count": 1},
            ],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(
            ["members"],
            expected=[
                {"service": "ftp", "port": 21, "protocol": Protocol.TCP.value, "count": 1},
                {"service": "https", "port": 443, "protocol": Protocol.TCP.value, "count": 1},
                {"service": "mysql", "port": 3306, "protocol": Protocol.TCP.value, "count": 1},
            ],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?target=1"),
    ]
