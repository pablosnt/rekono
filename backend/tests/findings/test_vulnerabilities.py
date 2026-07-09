from django.test import TestCase

from findings.enums import TransportProtocol, TriageStatus
from findings.models import Port, Technology, Vulnerability
from tests.findings.base import FindingTest
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types,attribute-error


class VulnerabilityTest(FindingTest, TestCase):
    model = Vulnerability
    endpoint = "/api/vulnerabilities/"
    expected_defectdojo = {
        "title": "Vulnerability 10",
        "description": "Vulnerability 10",
        "severity": "Medium",
        "cve": "CVE-2025-3010",
        "cwe": 200,
    }
    expected_string = (
        f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - WordPress - 1.0.10 - Vulnerability 10 - CVE-2025-3010"
    )
    sample_cve = "CVE-2025-9999"
    sample_name = "Already enriched finding"

    def test_deduplication_by_name(self):
        first = Vulnerability.objects.create_finding(self.execution, technology=self.technology, name=self.sample_name)
        second = Vulnerability.objects.create_finding(self.execution, port=self.port, name=self.sample_name)
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Vulnerability.objects.filter(technology=self.technology, name=self.sample_name).count())
        self.assertIsNone(second.port)
        self.assertEqual(self.technology, second.technology)

    def test_deduplication_with_same_technology(self):
        first = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_cve, cve=self.sample_cve
        )
        second = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_cve, cve=self.sample_cve
        )
        self.assertEqual(first.id, second.id)

    def test_deduplication_with_same_port(self):
        first = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name=self.sample_cve, cve=self.sample_cve
        )
        second = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name=self.sample_cve, cve=self.sample_cve
        )
        self.assertEqual(first.id, second.id)

    def test_deduplication_with_user_input(self):
        user_finding = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name=self.sample_cve, cve=self.sample_cve, created_from_user_input=True
        )
        detected_finding = Vulnerability.objects.create_finding(
            self.execution,
            port=self.port,
            technology=self.technology,
            name=self.sample_cve,
            cve=self.sample_cve,
            created_from_user_input=False,
        )
        self.assertEqual(user_finding.id, detected_finding.id)
        self.assertEqual(1, Vulnerability.objects.filter(port=self.port, cve=self.sample_cve).count())
        self.assertEqual(self.technology, detected_finding.technology)
        self.assertFalse(detected_finding.created_from_user_input)

    def test_deduplication_with_new_user_input(self):
        detected_finding = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_name, cve=self.sample_cve
        )
        user_finding = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name=self.sample_cve, cve=self.sample_cve, created_from_user_input=True
        )
        self.assertEqual(detected_finding.id, user_finding.id)
        self.assertEqual(self.sample_name, user_finding.name)
        self.assertEqual(1, Vulnerability.objects.filter(technology=self.technology, cve=self.sample_cve).count())
        self.assertEqual(self.technology, user_finding.technology)
        self.assertIsNone(user_finding.port)
        self.assertFalse(user_finding.created_from_user_input)

    def test_deduplication_with_new_port(self):
        tech_finding = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_cve, cve=self.sample_cve
        )
        port_finding = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name=self.sample_cve, cve=self.sample_cve
        )
        self.assertEqual(tech_finding.id, port_finding.id)
        self.assertIsNone(port_finding.port)
        self.assertEqual(tech_finding.technology, port_finding.technology)

    def test_deduplication_with_new_technology(self):
        port_finding = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name=self.sample_cve, cve=self.sample_cve
        )
        tech_finding = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_cve, cve=self.sample_cve
        )
        self.assertEqual(port_finding.id, tech_finding.id)
        self.assertIsNone(tech_finding.port)
        self.assertEqual(self.technology, tech_finding.technology)

    def test_deduplication_with_different_technologies_from_same_port(self):
        other_technology = Technology.objects.create_finding(
            self.execution, port=self.port, name="Apache", version="2.4.1"
        )
        first = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_cve, cve=self.sample_cve
        )
        second = Vulnerability.objects.create_finding(
            self.execution, technology=other_technology, name=self.sample_cve, cve=self.sample_cve
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Vulnerability.objects.filter(cve=self.sample_cve).count())
        Vulnerability.objects.create_finding(self.execution, port=self.port, name=self.sample_cve, cve=self.sample_cve)
        self.assertEqual(1, Vulnerability.objects.filter(cve=self.sample_cve).count())

    def test_deduplication_not_merged(self):
        algorithm_finding = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_name
        )
        cve_finding = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_cve, cve=self.sample_cve
        )
        self.assertNotEqual(algorithm_finding.id, cve_finding.id)

    def test_deduplication_different_ports_not_merged(self):
        other_port = Port.objects.create_finding(
            self.execution, host=self.host, port=8443, protocol=TransportProtocol.TCP
        )
        first = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name=self.sample_cve, cve=self.sample_cve
        )
        second = Vulnerability.objects.create_finding(
            self.execution, port=other_port, name=self.sample_cve, cve=self.sample_cve
        )
        self.assertNotEqual(first.id, second.id)

    def test_deduplication_different_technologies_on_different_ports_not_merged(self):
        other_port = Port.objects.create_finding(
            self.execution, host=self.host, port=8443, protocol=TransportProtocol.TCP
        )
        other_technology = Technology.objects.create_finding(
            self.execution, port=other_port, name="WordPress", version="1.0.0"
        )
        first = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name=self.sample_cve, cve=self.sample_cve
        )
        second = Vulnerability.objects.create_finding(
            self.execution, technology=other_technology, name=self.sample_cve, cve=self.sample_cve
        )
        self.assertNotEqual(first.id, second.id)


class LatestVulnerabilitiesTest(ApiTest, TestCase):
    endpoint = "/api/vulnerabilities/latest/"
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
