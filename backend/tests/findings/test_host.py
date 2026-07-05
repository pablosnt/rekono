from django.test import TestCase

from findings.enums import HostOS, Severity
from findings.models import Host
from tests.findings.base import FindingTest
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types,attribute-error


class HostTest(FindingTest, TestCase):
    model = Host
    endpoint = "/api/hosts/"
    expected_defectdojo = {
        "title": "Host discovered",
        "description": f"IP: 10.10.10.10\nOS type: {HostOS.LINUX.value}",
        "severity": Severity.INFO,
    }
    expected_string = "10.10.10.10"

    def test_deduplication(self):
        first = Host.objects.create_finding(self.execution, ip="10.10.10.60", os="Windows Server 2022")
        second = Host.objects.create_finding(self.execution, ip="10.10.10.60")
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Host.objects.filter(ip="10.10.10.60").count())
        self.assertEqual("Windows Server 2022", second.os)
        self.assertNotEqual(second.id, Host.objects.create_finding(self.execution, ip="10.10.10.61").id)

    def test_deduplication_with_user_input(self):
        user_finding = Host.objects.create_finding(self.execution, ip="10.10.10.62", created_from_user_input=True)
        detected_finding = Host.objects.create_finding(
            self.execution, ip="10.10.10.62", os="Ubuntu 22.04", created_from_user_input=False
        )
        self.assertEqual(user_finding.id, detected_finding.id)
        self.assertEqual(1, Host.objects.filter(ip="10.10.10.62").count())
        self.assertEqual("Ubuntu 22.04", detected_finding.os)
        self.assertFalse(detected_finding.created_from_user_input)

    def test_deduplication_with_new_user_input(self):
        detected_finding = Host.objects.create_finding(self.execution, ip="10.10.10.63", os="Debian 12")
        user_finding = Host.objects.create_finding(self.execution, ip="10.10.10.63", created_from_user_input=True)
        self.assertEqual(detected_finding.id, user_finding.id)
        self.assertEqual(1, Host.objects.filter(ip="10.10.10.63").count())
        self.assertEqual("Debian 12", user_finding.os)
        self.assertFalse(user_finding.created_from_user_input)


class LatestHostsTest(ApiTest, TestCase):
    endpoint = "/api/hosts/latest/"
    data = [SetupProject(2, 6)]
    cases = [
        ApiTestCase(["members"], expected=[{"id": value} for value in range(1, 6)]),
        ApiTestCase(["not_members"]),
        ApiTestCase(["members"], expected=[{"id": value} for value in range(1, 6)], endpoint="{endpoint}?project=1"),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(["members"], expected=[{"id": value} for value in range(1, 6)], endpoint="{endpoint}?target=1"),
        ApiTestCase(["members"], expected=[{"id": value} for value in range(7, 12)], endpoint="{endpoint}?target=2"),
        ApiTestCase(["not_members"], endpoint="{endpoint}?target=2"),
    ]
